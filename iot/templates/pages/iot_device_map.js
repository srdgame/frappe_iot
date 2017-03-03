frappe.ready(function() {
	var map = new BMap.Map("baiduMap");
	map.centerAndZoom(new BMap.Point(116.404, 39.915), 4);
	map.enableScrollWheelZoom();

	var MAX = 10;
	var markers = [];
	var pt = null;
	var i = 0;
	for (; i < MAX; i++) {
	   pt = new BMap.Point(Math.random() * 40 + 85, Math.random() * 30 + 21);
	   markers.push(new BMap.Marker(pt));
	}
	//最简单的用法，生成一个marker数组，然后调用markerClusterer类即可。
	var markerClusterer = new BMapLib.MarkerClusterer(map, {markers:markers});
});