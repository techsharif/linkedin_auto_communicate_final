

	
$(document).ready(function() {
	var url = window.location.href;
	var statusColors = {
		"0": "btn-purple",
		"22": "bg-maroon",
		"21": "bg-gray",
		"10": "bg-green",
		"12": "bg-yellow",
		"200": "bg-default",
		"3": "bg-default",
		"1": "bg-default",
		"23": "bg-default",
		"20": "bg-default",
		"7": "bg-default",
		"100": "bg-default",
		"6": "bg-default",
		"28": "bg-green",
	};
	var path = window.location.pathname;
	var inboxPage = path.indexOf('network')>=0? false: true;
	var status_index = 8;
	
    var table = $('#campaign_people').DataTable( {
        "ajax": url,
        'initComplete': function(settings){
            var api = this.api();
			/* disale the disable checkbox now
            api.cells(
               api.rows(function(idx, data, node){
            	  //inqueue
                  return (data[status_index] === 0) ? true : false;
               }).indexes(),
               0
            ).checkboxes.disable();
			*/
            // filer by colums
            api.columns().every( function () {
                var column = this;
                if (column.index() === status_index){
                	//console.log(column.data());
                    var select = $('<select><option value=""></option></select>')
                        .appendTo( $(column.header()) )
                        .on( 'change', function () {
                            var val = $.fn.dataTable.util.escapeRegex(
                                $(this).val()
                            );
                            var text = contact_statuses[val];
     						console.log('text:', val, text);
                            column
                                .search( (val && val >= 0) ? text  : '', false, true )
                                .draw();
                        } );
     				var status_list = inboxPage? contact_statuses: mynetwork_statuses;
                    Object.keys(status_list).sort().forEach(function(k) {
                    	select.append( '<option value="'+ k +'">'+ contact_statuses[k] +'</option>' );
                    })
                }
                
            } );
         },
        'columnDefs': [
            {
               'targets': 0,
               'checkboxes': true
            },
            {
                "targets": status_index,
                "data": null,
                "render": function ( data, type, row ) {
                	var v =  row[status_index];
                	var btncolor = statusColors[v]? statusColors[v]: 'bg-maroon';
                	
                    var html = '<span data-status="'+ v +'" data-contactid="'+ row[0] +'" class="btn '+ btncolor;
                    html+= ' btn-block" data-click="change_status" data-toggle="tooltip"';
                    html+= 'data-html="true" title="';
                    if (v === 22){
                    	html+= '<strong>Imported</strong><br>';
                        html+= 'Old contact before you joined B2B';
                    }else if (v === 0){
                    	html+= '<strong>'+ row[7] + '</strong>';
                    }
                    html+= '<br><i>Click on status to change it manually</i>">';
                    html+= contact_statuses[v];
                    html+= '</span>';
                    
                    return html;
                },
            },
            {
                "targets": [ 7 ], //
                "visible": !inboxPage,
                "searchable": true,
                "render": function(data, type, row){
                	var extrahtml =  "";
                	if (row[9] === true)
                		extrahtml =  "messenger";
                	else if (row[9] === false)
                		extrahtml =  "connector";
                	
                	extrahtml = (row[7]!== null?row[7]:"") + '<span class="hidden">' + extrahtml + '</span>';
                	return extrahtml;
                }
            },
            {
                "targets": [ 9 ], //
                "visible": false,
                "searchable": false,
                
            },
         ],
         'order': [[1, 'asc']],
         
         "drawCallback": function( settings ) {
        	 var popover = '<div class="list-group" style="margin:0" data-cid="{{pk}}">';
        	 var status = ['Later', 'No Interest', 'Replied', 'Talking', 'Old Connect']
        		popover+= '<a href="#" data-status="20" data-click="changeStatus" class="list-group-item ">Mark Later</a>';
        		popover+= '<a href="#" data-status="21" data-click="changeStatus" class="list-group-item bg-gray ">Mark No Interest</a>';
        		popover+= '<a href="#" data-status="10" data-click="changeStatus" class="list-group-item bg-green ">Mark Replied</a>';
        		popover+= '<a href="#" data-status="12" data-click="changeStatus" class="list-group-item bg-yellow ">Mark Talking</a>';
        		popover+= '<a href="#" data-status="22" data-click="changeStatus" class=" list-group-item bg-maroon">Mark Old Connect</a>';
        		popover+= '</div>';
        	 $('[data-toggle="tooltip"]').tooltip();
        	 $('[data-click="change_status"]').popover({
        		 template: popover,
        		 placement: 'bottom',
        		 target: 'body'
        	 });
        	
          },
          "dom": '<"toolbar col-md-8 mt-sm mb-sm pull-left">frtip'
        
    } );
    
    
	var header_buttons = '';
	if(inboxPage){
		//inbox page
		
		header_buttons+= '<button class="btn btn-default mr" data-click="markRead">Mark as read</button>';
		header_buttons+= '<button class="btn btn-default mr" data-click="markUnread">Mark as unread</button>';
		header_buttons+= '<button class="btn btn-default mr" data-click="removeFromCampaign" data-cid="1">Delete</button>';
		
	}else if (path.indexOf('network')>=0){
		//network page
		
		header_buttons+= '<span class="btn btn-default btn-datafilter mr-lg mb-lg"><input  type="checkbox" data-click="connector">&nbsp;&nbsp;Show Connector contacts</span>';
		header_buttons+= '<span class="btn btn-default btn-datafilte mr-lg mb-lg"><input  type="checkbox" data-click="messenger">&nbsp;&nbsp;Show Messenger contacts</span>';
		header_buttons+= '<span class="btn btn-default btn-datafilte mr-lg mb-lg"><input  type="checkbox" data-click="talking">&nbsp;&nbsp;Show Talking contacts</span>';
		header_buttons+= '<a class="btn btn-default mr" id="add_selected" data-click="addSelected2Campaign">Add selected contacts to Messenger Campaign</a>';
		header_buttons+= '<a class="btn btn-default mr" id="add_allnew" data-click="addAll2Campaign">Add all filtered contacts to Messenger Campaign</a>';
	}
	// plus csv export
	header_buttons+= '<button class="btn btn-default export-to-csv" title="Export contacts to CSV"><i class="fa fa-file-excel-o"></i></button>';
	
	$("div.toolbar").html(header_buttons);
	$(".dataTables_filter").addClass("col-md-3 mt-sm  mb-sm");
    
	$('section.content').on('click', 'input[data-click="connector"], input[data-click="messenger"]', function(e){
		//campaign with is_bulk true or false
		var that = $(this);
		var val = that.data('click');
		var column = table.column( 7 );
		column.search( that.is(':checked')? val:'' , false, true )
        .draw();
		
	});
	$('section.content').on('click', 'input[data-click="talking"]', function(e){
		var that = $(this);
		// check?
		var column = table.column( 8 );
		column.search( that.is(':checked')?contact_statuses[12]:'' , false, true )
        .draw();
	});
	
    $('table').on('click', 'a[data-click="changeStatus"]', function(e){
        if($('.popoverButton').length>1)
	        $('.popoverButton').popover('hide');
	    $(e.target).popover('toggle');
	    
	    var parent = $(this).parent();
	    parent.popover('hide');
	    var statusbox = parent.prev();
	    var contactid = statusbox.data('contactid');
	    var old_status = statusbox.data('status');
	    var new_status = $(this).data('status');
	    changeContactStatus(contactid, new_status, old_status, function(contactid, new_status, old_status){
	    	
	    	var oldcolor = statusColors[old_status];
	    	var newcolor = statusColors[new_status];
	    	console.log('changing status:', old_status, oldcolor, newcolor, new_status);
	    	spanbox = $('td>span[data-contactid="' + contactid + '"]');
	    	spanbox.text(contact_statuses[new_status]);
	    	spanbox.removeClass(oldcolor).addClass(newcolor);
	    	
	    });
	    
    });
    
    function changeContactStatus(contactid, new_status, old_status, cb){
    	var url = "/account/contact/" + contactid + "/status?status="+new_status;
    	$.get(url).done(function(res){
    		
    		if (res.ok){
    			cb(contactid, new_status, old_status);
    		}
    	})
    }
    
	// buton click
	//export to excel
	$('button[data-click="export"]').click(function(e){
		swal("alert!", "Will be done.", "success");
		
	});
	//delete
	$('button[data-click="removeFromCampaign"]').click(function(e){
		var rows_selected = table.column(0).checkboxes.selected();
		if(rows_selected.length < 1){
			alert_no_contact();
    		return;
		}
		console.log('rows_selected:', rows_selected);
		swal({
			  title: "Are you sure?",
			  text: "Your connect contacts will be deleted but your network contats will be changed to 'Old connect'",
			  type: "warning",
			  showCancelButton: true,
			  confirmButtonClass: "btn-danger",
			  confirmButtonText: "Yes, delete it!",
			  closeOnConfirm: false
			},
			function(){
				var form = $('form[name="contacts-delete"]');
				
				var data = rows_selected.join(',');
				form.find('input[name="cid"]').val(data);
				do_post_action(form, function(){
					table.ajax.reload();
					swal("Deleted!", "Your contacts have been deleted.", "success");
				});
					
				
			  
			});
	});
	
	//add selected
    $('#add_selected').click( function(e){
    	
    	var rows_selected = table.column(0).checkboxes.selected();
    	var contacts = [];
    	$.each(rows_selected, function(index, rowId){
    		contacts.push(rowId);
    		// find its row
    		var $row = $('td>span[data-contactid="'+ rowId + '"]').closest('tr');    	    // Get row data
    	      var row = table.row($row).data();
    		if (row){
    			console.log('row:', row);
       			if (row[7] !== null)
           			contact_camps[row[7]] = 1;
    		}
    		
    	});
    	if (contacts.length == 0){
    		// alert
    		//alert('No contact has been selected!');
    		alert_no_contact();
    		return;
    	}
    	// show campain modal
    	show_add2campaign(contacts);
    });
	
	function alert_no_contact(){
		swal("Alert!", "No selected contact", "error");
	};
	
	//add_all filtered contact
	
	$('#add_allnew').click( function(e){
    	
    	if( filtered_row_num < 1) {
    		alert_no_contact();
    		return;
    	}
    	var contacts = [];
    	$.each(filtered_rows, function(index, row){
    		contacts.push(row[0]);
    		if (row[7] !== null)
    			contact_camps[row[7]] = 1;
    	});
    	show_add2campaign(contacts);
    	
    	
    });
    function show_add2campaign(contacts) {
    	var cids = contacts.join(',');
    	$('#add2campaign input[name="cid"]').val(cids);
    	$("#add2campaign").modal('show');
    	
    }
	
	//add2bulk_button
	$('body').on('click', '.add2bulk_button', function (e) {
		e.preventDefault();
		var that = $(this);
		// check campaign message
		var selected_camp = $("#add2campaign #campaign option:selected");
		var camp_id = selected_camp.val();
		var campaign_name = selected_camp.text();
		var messenger = $("#add2campaign .campaign-"+camp_id);
		var camp_message = messenger.html();
		if (camp_message === "" || camp_message.length < 5){
			var url = messenger.data('url');
			
			var text = 'Your selected campaign <b>' + campaign_name + '</b> has not had any message yet.';
			text+= ' Please add some <a href="' + url +'">here</a>.';
			
			show_camp_alert(text)
			return;
		}
		
    	// check contact in other campaign
    	
		console.log('campaign_name:', campaign_name, contact_camps);
		var othercamps = [];
		var arr = Object.keys(contact_camps);
		if (arr.length > 0){
			arr.forEach(function(camp) {
				console.log('checking:', camp);
			
				if (camp !== campaign_name){
					othercamps.push(camp);
				}
					
			});
			
			console.log('othercamps:', othercamps);
			if (othercamps.length > 0){
				// add move contacts button
				
				var text = 'Contacts in <b>'+ othercamps.join(', ') + '</b> campaign' + (othercamps.length>1?'s':'');
				text+= ' will be moved into <b>' + campaign_name + '</b>';
				
				show_camp_alert(text);
				$("#add2campaign .move2bulk_button").removeClass('hidden');
				
				return;
			}
		}
		do_post_campaign(that);
		
		
	
	} );
	$('body').on('click', '.move2bulk_button', function (e) {
		e.preventDefault();
		var that = $(this);
		do_post_campaign(that);
		
	});
	function show_camp_alert(text){
		$("#add2campaign .add2bulk_button").hide();
		$("#add2campaign .modal-body-input").hide();
		var mbody = $("#add2campaign .modal-body-move");
		
		mbody.html(text);
		mbody.show();
	}
	function do_post_campaign(that){
		var form = that.closest('form');
		do_post_action(form, function(){
			table.ajax.reload();
			$("#add2campaign").modal('hide');
		});
		
	}
	
	function do_post_action(form, cb){
    	var data = form.serialize();
    	console.log('posted data:', form.attr('action'),  data);
		$.post(form.attr('action'), data).done(function(res){
			console.log('posted result:', data);
			if(res.ok){				
				cb(res);
			}
		});
	}
	
	// filtered
	table.on('search.dt', function() {
	    //number of filtered rows
	    filtered_row_num = table.rows( { filter : 'applied'} ).nodes().length;
	    //filtered rows data as arrays
	    filtered_rows = table.rows( { filter : 'applied'} ).data();                                  
	}) 
    
    // click row
	$('#campaign_people tbody').on('click', 'tr', function () {
        var data = table.row( this ).data();
        show_uinfo(data[0])
    } );
	var current_uid = 1;
	function show_uinfo(uid){
		current_uid = uid;
		var url = "/messenger/contact/" + uid + "/updatenote";
		$.get(url).done(function(res){
			$('#uinfo_box').html(res);
		});
	}
	
	//save notes
	$('body').on('click', '#save_notes', function(e){
		e.preventDefault();
		var form = $(this).closest('form');
		do_post_action(form, function(){console.log('notes is saved')});
	});
	//sendmessage
	$('body').on('click', '#sendmessage', function(e){
		e.preventDefault();
		var form = $(this).closest('form');
		do_post_action(form, function(res){
			console.log('notes is saved')
			show_uinfo(current_uid);
			
			});
	});
	
	setTimeout(function(){
		var firstrow = $('#campaign_people tbody tr').first();
		var data = table.row( firstrow ).data();
		if( data)
        	show_uinfo(data[0])
	}, 2000);
	
	
	
	// for collapse chat content
	$("body").on('click', "[data-widget='collapse']", function(e) {
		console.log('data widget');
	    //Find the box parent........
	    var box = $(this).parents(".box").first();
	    //Find the body and the footer
	    var bf = box.find(".box-body, .box-footer");
	    if (!$(this).children().hasClass("fa-plus")) {
	        $(this).children(".fa-minus").removeClass("fa-minus").addClass("fa-plus");
	        bf.slideUp();
	    } else {
	        //Convert plus into minus
	        $(this).children(".fa-plus").removeClass("fa-plus").addClass("fa-minus");
	        bf.slideDown();
	    }
	});
	
});