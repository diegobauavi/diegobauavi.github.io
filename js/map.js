(function () {
  "use strict";

  var el = document.getElementById("travel-map");
  if (!el || typeof jsVectorMap === "undefined") return;

  // Countries visited (ISO 3166-1 alpha-2).
  var VISITED = [
    "CL", "AR", "MX", "BR", "US", "CA", "ES", "FR", "GB", "IT", "CH",
    "NL", "AT", "SI", "SK", "TN", "HU", "TR", "DE", "HR", "ME", "CZ"
  ];

  // Theme-neutral palette: these read well on both the light and dark
  // backgrounds, so the map never needs to be rebuilt when the theme changes.
  var VISITED_FILL = "#e8a13a"; // amber
  var REST_FILL = "#b4bac4";    // un-visited countries
  var BORDER = "#8b92a0";       // separates countries

  var map = null;

  function build() {
    if (map) return;
    map = new jsVectorMap({
      selector: "#travel-map",
      map: "world",
      zoomButtons: true,
      zoomOnScroll: false,
      regionsSelectable: false,
      backgroundColor: "transparent",
      regionStyle: {
        initial: { fill: REST_FILL, stroke: BORDER, strokeWidth: 0.4, fillOpacity: 1 },
        hover: { fillOpacity: 0.7 },
        selected: { fill: VISITED_FILL },
        selectedHover: { fillOpacity: 0.8 }
      }
    });
    if (map.setSelectedRegions) map.setSelectedRegions(VISITED);
  }

  // The map lives inside the (initially hidden) Personal panel, so build it the
  // first time it actually becomes visible, then just resize on later reveals.
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      if (!map) build();
      else if (map.updateSize) map.updateSize();
    });
  });
  io.observe(el);

  window.addEventListener("resize", function () {
    if (map && map.updateSize) map.updateSize();
  });
})();
