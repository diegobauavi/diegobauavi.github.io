(function () {
  "use strict";

  var el = document.getElementById("travel-map");
  if (!el || typeof jsVectorMap === "undefined") return;

  // Countries visited (ISO 3166-1 alpha-2).
  var VISITED = [
    "CL", "AR", "MX", "BR", "US", "CA", "ES", "FR", "GB", "IT", "CH",
    "NL", "AT", "SI", "SK", "TN", "HU", "TR", "DE", "HR", "ME"
  ];

  var VISITED_FILL = "#e8a13a"; // amber, reads on both light and dark themes
  var visitedValues = {};
  VISITED.forEach(function (code) { visitedValues[code] = VISITED_FILL; });

  function isDark() {
    return document.documentElement.getAttribute("data-theme") === "dark";
  }

  function isVisible() {
    return el.offsetParent !== null && el.clientWidth > 0;
  }

  var map = null;

  function build() {
    if (map) { map.destroy(); map = null; }
    var rest = isDark() ? "#39404e" : "#d4d8e0";   // un-visited fill
    var line = isDark() ? "#14151a" : "#ffffff";   // borders separate countries
    map = new jsVectorMap({
      selector: "#travel-map",
      map: "world",
      zoomButtons: true,
      zoomOnScroll: false,
      regionsSelectable: false,
      backgroundColor: "transparent",
      regionStyle: {
        initial: { fill: rest, stroke: line, strokeWidth: 0.4, fillOpacity: 1 },
        hover: { fillOpacity: 0.7 }
      },
      series: {
        regions: [{ attribute: "fill", values: visitedValues }]
      }
    });
  }

  // The map lives inside the (initially hidden) Personal panel, so build it the
  // first time it actually becomes visible, then just resize on later reveals.
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      if (!map) {
        build();
      } else if (map.updateSize) {
        map.updateSize();
      }
    });
  });
  io.observe(el);

  // Rebuild on theme change so un-visited countries match the palette.
  new MutationObserver(function (mutations) {
    mutations.forEach(function (m) {
      if (m.attributeName === "data-theme" && map) {
        build();
        if (isVisible() && map.updateSize) map.updateSize();
      }
    });
  }).observe(document.documentElement, { attributes: true });

  window.addEventListener("resize", function () {
    if (map && map.updateSize) map.updateSize();
  });
})();
