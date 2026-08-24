function copyQuickstart() {
  const code = `git clone git@github.com:el-j/run-zero.git
cd run-zero && make env
make start
make logs`;

  navigator.clipboard.writeText(code).then(() => {
    const btn = document.querySelector('.copy-btn');
    if (btn) {
      const originalText = btn.textContent;
      btn.textContent = 'Copied!';
      setTimeout(() => {
        btn.textContent = originalText;
      }, 2000);
    }
  });
}
