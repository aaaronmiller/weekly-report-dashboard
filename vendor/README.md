# Vendor

- ECharts 5.5.1 minified build from jsDelivr CDN: https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js
- SHA-256: e84270bd0cd5bdf60fefc26d00c2a391cb2e81f4d26a7a9ee16185a54773a3cf
- Size: 1007K
- Inlined into index.html at build time; never fetched at runtime (NFR-020).

Performance (measured 2026-08-08):
- Full build (6 bundles, 12 weeks): ~0.4s
- Page weight: ~1.1 MB (vendor dominates)
