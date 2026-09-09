const videos = Array.from(document.querySelectorAll('video'));
const playAll = () => videos.forEach(video => {
  video.muted = true; video.defaultMuted = true;
  if (video.paused) video.play().catch(() => {});
});
videos.forEach(video => video.addEventListener('canplay', playAll));
document.addEventListener('visibilitychange', playAll);
document.addEventListener('pointerdown', playAll, { once: true });
playAll();
document.getElementById('copy-citation').addEventListener('click', async event => {
  try { await navigator.clipboard.writeText("@inproceedings{ye2026instanthdr,\n  title     = {InstantHDR: Single-Forward Gaussian Splatting\n               Initialization for HDR 3D Reconstruction},\n  author    = {Ye, Dingqiang and Xu, Jiacong and Ping, Jianglu and\n               Guo, Yuxiang and Fan, Chao and Patel, Vishal M.},\n  booktitle = {Computer Vision -- ECCV 2026},\n  year      = {2026},\n  publisher = {Springer}\n}"); event.target.textContent = 'Copied'; }
  catch { event.target.textContent = 'Select text below'; }
});
