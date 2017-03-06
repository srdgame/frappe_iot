frappe.ready(function() {
	var map = new BMap.Map("baiduMap");
	map.centerAndZoom(new BMap.Point(116.404, 39.915), 4);
	map.enableScrollWheelZoom();

	var opts = {
		width : 250,     // 信息窗口宽度
		height: 160,     // 信息窗口高度
		//title : "设备信息" , // 信息窗口标题
		enableMessage:true//设置允许信息窗发送短息
	};
	function addClickHandler(content,marker){
		marker.addEventListener("click",function(e){
			openInfo(content,e)}
		);
	}
	function openInfo(content,e){
		var p = e.target;
		var point = new BMap.Point(p.getPosition().lng, p.getPosition().lat);
		var infoWindow = new BMap.InfoWindow(content,opts);  // 创建信息窗口对象
		map.openInfoWindow(infoWindow,point); //开启信息窗口
	}

	frappe.call({
		type: "GET",
		method: "iot.iot.doctype.iot_device.iot_device.list_device_map",
		callback: function(r) {
			if(!r.exc) {
				if(r._server_messages)
					frappe.msgprint(r._server_messages);
				else {
					var markers = [];
					var devices = r.message;
					for (var dev in devices) {
						pt = new BMap.Point(devices[dev].longitude, devices[dev].latitude);
						var marker = new BMap.Marker(pt);
						var content = "<h4 style='margin:0 0 5px 0;padding:0.2em 0'>" +
							devices[dev].dev_name + "</h4>" +
							"<p> Status : " + devices[dev].device_status + "</p>" +
							"<p> Last Updated : " + devices[dev].last_updated + "</p>" +
							"<a href='/iot_devices/" + devices[dev].sn + "'>Detials</a>";

						alert(content);

						addClickHandler(content, marker);
						markers.push(marker);
					}
					//最简单的用法，生成一个marker数组，然后调用markerClusterer类即可。
					var markerClusterer = new BMapLib.MarkerClusterer(map, {markers: markers});
				}
			} else {
				if(r._server_messages)
					frappe.msgprint(r._server_messages);
				else
					frappe.msgprint(r.message);
			}
		}
	});
});