(function () {
  if (!window.webVitals) return;
  function sendMetric(metric) {
    try {
      fetch('/api/metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        keepalive: true,
        body: JSON.stringify({
          name: metric.name,
          value: metric.value,
          rating: metric.rating,
          id: metric.id,
          nav: location.pathname,
        }),
      });
    } catch {}
  }
  webVitals.onINP(sendMetric);
  webVitals.onTTFB(sendMetric);
  webVitals.onCLS(sendMetric);
})();


