frappe.ready(function() {
	var map = new BMap.Map("baiduMap");
	map.centerAndZoom(new BMap.Point(116.404, 39.915), 4);
	map.enableScrollWheelZoom();

	var opts = {
		width : 250,     // 信息窗口宽度
		height: 80,     // 信息窗口高度
		title : "信息窗口" , // 信息窗口标题
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
						var sContent = 	"<h4 style='margin:0 0 5px 0;padding:0.2em 0'>" + devices[dev].name + "</h4>" +
										"<a href='/iot_devices/'" + devices[dev].sn + "'>Detials</a>";

						addClickHandler(content, marker);
						markers.push(marker);
					}
					//最简单的用法，生成一个marker数组，然后调用markerClusterer类即可。
					var markerClusterer = new BMapLib.MarkerClusterer(map, {markers: markers});
				}

				var data_info = [[116.417854,39.921988,"地址：北京市东城区王府井大街88号乐天银泰百货八层"],
					 [116.406605,39.921585,"地址：北京市东城区东华门大街"],
					 [116.412222,39.912345,"地址：北京市东城区正义路甲5号"]
					];
				for(var i=0;i<data_info.length;i++) {
					var marker = new BMap.Marker(new BMap.Point(data_info[i][0], data_info[i][1]));  // 创建标注
					var content = data_info[i][2];
					map.addOverlay(marker);               // 将标注添加到地图中
					addClickHandler(content, marker);
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