var refflag = 0;
var symlinksn = '{{ doc.sn }}';
var devices = {{ vsn }};
var id = '';
var rtvalueurl = ';'

console.log(symlinksn);
console.log(devices);


frappe.ready(function() {
    var rtvalueurl = "/api/method/iot.hdb.iot_device_data_array?sn=" + symlinksn;
    var table = jQuery('#example').DataTable({
        "dom": 'lfrtp',
        //"bInfo" : false,
        //"pagingType": "full_numbers" ,
        "ajax": {
            "url": rtvalueurl,
            //"url": "/api/method/tieta.tieta.doctype.cell_station.cell_station.list_station_map",
            "dataSrc": "message",
        },
        "columns": [
            {"data": "NAME"},
            {"data": "DESC"},
            {"data": "TM"},
            {"data": "PV"},
            {"data": "Q"},


        ]
    });

      refflag = setInterval( function () {table.ajax.reload( null, false ); }, 3000 );

    //点击按钮
          $("div .btn").each(function(){
              $(this).click(function(){
                  name = $(this).attr("devname");
                  id = $(this).attr("devid");
                  console.log(name, id);
                  if(id==symlinksn){
                      var rtvalueurl = "/api/method/iot.hdb.iot_device_data_array?sn=" + symlinksn;
                  }
                  else{
                      var rtvalueurl = "/api/method/iot.hdb.iot_device_data_array?sn=" + symlinksn + "&vsn=" + id;
                  }

                  console.log(rtvalueurl);
                  table.ajax.url(rtvalueurl).load();
                    $($(this).siblings()).removeClass('btn-success');
                    $(this).addClass('btn-success');
                    $('#devname').html("{{_('NAME:')}}"+name);
                    $('#devsn').html("{{_('SN:')}}"+id);
              });
          });
    //点击按钮
});


