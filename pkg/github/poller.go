package github

import (
	"context"
	"fmt"
	"sync"
	"time"

	"github.com/el-j/run-zero/pkg/state"
)

// Poller polls configured repositories for queued workflow jobs and updates live fleet state.
type Poller struct {
	client       *Client
	reconciler   *Reconciler
	state        *state.State
	repos        []string
	pollInterval time.Duration
	concurrency  int
}

// NewPoller creates an autoscaler poller.
func NewPoller(
	client *Client,
	reconciler *Reconciler,
	st *state.State,
	repos []string,
	pollInterval time.Duration,
) *Poller {
	if pollInterval <= 0 {
		pollInterval = 10 * time.Second
	}
	cleanedRepos := make([]string, 0, len(repos))
	for _, r := range repos {
		if r != "" {
			cleanedRepos = append(cleanedRepos, r)
		}
	}
	return &Poller{
		client:       client,
		reconciler:   reconciler,
		state:        st,
		repos:        cleanedRepos,
		pollInterval: pollInterval,
		concurrency:  4,
	}
}

// PollOnce executes a single poll cycle across all tracked repositories.
func (p *Poller) PollOnce(ctx context.Context) error {
	var mu sync.Mutex
	var allJobs []state.QueuedJob
	var pollErrors []error

	sem := make(chan struct{}, p.concurrency)
	var wg sync.WaitGroup

	for _, repo := range p.repos {
		wg.Add(1)
		go func(r string) {
			defer wg.Done()
			select {
			case sem <- struct{}{}:
				defer func() { <-sem }()
			case <-ctx.Done():
				return
			}

			jobs, err := p.client.ListQueuedJobs(ctx, r)
			mu.Lock()
			defer mu.Unlock()
			if err != nil {
				pollErrors = append(pollErrors, fmt.Errorf("repo %s: %w", r, err))
				return
			}
			allJobs = append(allJobs, jobs...)
		}(repo)
	}

	wg.Wait()

	rl := p.client.RateLimit()
	if rl.Limit > 0 {
		rem := rl.Remaining
		lim := rl.Limit
		p.state.SetRateLimit(&rem, &lim)
	}

	snap := p.state.GetSnapshot()
	reconciled := p.reconciler.Reconcile(allJobs, snap.BusyRunners, snap.MaxRunners)
	p.state.UpdateFleet(snap.Runners, reconciled)

	if len(pollErrors) > 0 {
		return fmt.Errorf("poller completed with %d error(s): %v", len(pollErrors), pollErrors[0])
	}
	return nil
}

// Start begins periodic polling until ctx is canceled.
func (p *Poller) Start(ctx context.Context) {
	_ = p.PollOnce(ctx)

	ticker := time.NewTicker(p.pollInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			_ = p.PollOnce(ctx)
		}
	}
}
