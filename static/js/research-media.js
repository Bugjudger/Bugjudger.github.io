/* Poster-first animations, activated by hovering a paper or tapping its image. */
(() => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const hasHover = window.matchMedia('(hover: hover)');
  const assets = new Map();
  const load = (source) => {
    if (!assets.has(source)) {
      assets.set(source, fetch(source).then((response) => {
        if (!response.ok) throw new Error('Preview unavailable');
        return response.blob();
      }).catch((error) => {
        assets.delete(source);
        throw error;
      }));
    }
    return assets.get(source);
  };
  // Download animation bytes only after an intentional hover or tap.
  document.querySelectorAll('img[data-animated]').forEach((image) => {
    const card = image.closest('.pub-card');
    if (!card) return;
    let playing = false;
    let request = 0;
    let objectURL;
    const show = (active) => {
      playing = active && !reducedMotion.matches;
      const current = ++request;
      image.src = image.dataset.still;
      if (objectURL) URL.revokeObjectURL(objectURL);
      objectURL = undefined;
      image.setAttribute('aria-pressed', String(playing));
      if (!playing) return;
      // Cache the bytes, but give each activation a fresh animation timeline.
      // Keep the poster visible until the first frame is decoded.
      load(image.dataset.animated).then(async (blob) => {
        if (current !== request) return;
        const url = URL.createObjectURL(blob);
        const firstFrame = new Image();
        firstFrame.src = url;
        try {
          await firstFrame.decode();
          if (current !== request) {
            URL.revokeObjectURL(url);
            return;
          }
          objectURL = url;
          image.src = url;
        } catch (error) {
          URL.revokeObjectURL(url);
          if (current === request) show(false);
        }
      }).catch(() => {
        if (current === request) show(false);
      });
    };
    card.addEventListener('pointerenter', (event) => {
      if (event.pointerType === 'mouse' && hasHover.matches) show(true);
    });
    card.addEventListener('pointerleave', (event) => {
      if (event.pointerType === 'mouse') show(false);
    });
    image.addEventListener('click', () => {
      if (!hasHover.matches) show(!playing);
    });
    image.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        show(!playing);
      }
    });
    image.addEventListener('blur', () => show(false));
    reducedMotion.addEventListener('change', () => show(false));
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) show(false);
    });
  });
})();
