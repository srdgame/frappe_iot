var refflag = 0;
var symlinksn = '{{ doc.sn }}';
var devices = {{ vsn }};
var id = '';
var isvsn = false;
var current_vsn = '';
var rtvalueurl = ';';

console.log(symlinksn);
console.log(devices);


frappe.ready(function() {
    var rtvalueurl = "/api/method/iot.hdb.iot_device_data_array?sn=" + symlinksn;
    var table = jQuery('#example').DataTable({
        "dom": 'lfrtp',
        //"bInfo" : false,
        //"pagingType": "full_numbers" ,
        "bStateSave": true,
        "sPaginationType": "full_numbers",
        "iDisplayLength" : 25,
        "ajax": {
            "url": rtvalueurl,
            //"url": "/api/method/tieta.tieta.doctype.cell_station.cell_station.list_station_map",
            "dataSrc": "message",
        },
        "oLanguage": {
            "sLengthMenu": "每页显示 _MENU_ 条记录",
             "sZeroRecords": "抱歉， 没有找到",
            "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
            "sInfoEmpty": "没有数据",
            "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
            "oPaginate": {
                        "sFirst": "首页",
                        "sPrevious": "前一页",
                        "sNext": "后一页",
                        "sLast": "尾页"
                        },
            "sZeroRecords": "没有检索到数据",
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
                      isvsn = false;
                      current_vsn = '';
                  }
                  else{
                      var rtvalueurl = "/api/method/iot.hdb.iot_device_data_array?sn=" + symlinksn + "&vsn=" + id;
                      isvsn = true;
                      current_vsn = id;
                  }

                  console.log(rtvalueurl);
                  table.ajax.url(rtvalueurl).load();
                    $($(this).siblings()).removeClass('btn-success');
                    $(this).addClass('btn-success');
                    $('#devname').html("{{_('Name')}}"+":"+name);
                    $('#devsn').html("{{_('SN')}}"+":"+id);
              });
          });
    //点击按钮

    //双击表格行
      $('#example tbody').on('dblclick', 'tr', function () {
        var data = table.row( this ).data();
        tnm = data['NAME'].toLowerCase();
        console.log(isvsn);
        console.log(current_vsn);
        console.log(tnm);
        //window.location.href="/S_Station_infox/"+data['name'];

          if(isvsn){

            hisdataurl = "/iot_tag_his?sn="+symlinksn+"&vsn="+ current_vsn +"&tag="+tnm;
          }
          else{
            hisdataurl = "/iot_tag_his?sn="+symlinksn+"&tag="+tnm;
                  }
              console.log(hisdataurl);
              window.open(hisdataurl);

    } );
    //双击表格行tooltip({html : true }
    //$(function () { $('table .tooltip-show').tooltip('show');});
    $(function () { $("table.tooltip-options").tooltip({html : true });});
});


