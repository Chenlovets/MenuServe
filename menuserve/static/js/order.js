
$(document).ready(
	setInterval(function(){ getSubmittedOrder()}, 5000)
	);

function getSubmittedOrder() {

	var location = $('#dropdownMenuButton').text();
	console.log(location);

	$.ajax({
        url: '/getSubmittedOrder/',
        type: "POST",
        data: { 'location': location },
        success: function (data) {
            refreshOrder(data)
        },
        failure: function (data) {
            alert('Got an error dude');
        }
    });
}

function refreshOrder (data) {

	var num = data.num;
	console.log(num);
	var previous = $('#num').attr('value');
	console.log(previous);
	var previous_order = [];

	$(".pk").each(function() {
        previous_order.push(this.value);
    });

	if (num != previous){

		var pk_list = [];
		var fields_list = {};

		$.each(JSON.parse(data.orders), function(key, val) {
			pk_list.push(val.pk);

			var item_fields ={};
			$.each(val.fields, function(fieldname, field) {
                 item_fields[fieldname] = field;
            });
            
            fields_list[val.pk] = item_fields;  
        });

		var item_dict = JSON.parse(data.records);

		var html = "";

		var new_order =[];

		console.log("***pk_list***");
		console.log(pk_list);

		for ( order in pk_list) {
			console.log("***order***");
			console.log(order);

			if (!previous_order.includes(pk_list[order].toString())) {

				new_order.push(pk_list[order])
				var fields = fields_list[pk_list[order]]
				previous = parseInt(previous) + 1
				var items = ""
				var d = item_dict[pk_list[order]]
				for (var key in d ) {
					items += key
					items += ' x '
					items += d[key]
					items += '<br>'
				}
				text = '<tr>' + '<td>'+ previous + '</td>' + 
				'<td class="col-md-4 text-center">' + items + '</td>' +
				'<td class="col-md-2">$' + fields['total'] + '</td>' + 
              '<td class="col-md-2 text-center">' +
                '<div class="dropdown">' +
                  '<button class="btn btn-secondary btn-sm dropdown-toggle" type="button" id="dropdownMenuButton2" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">' +
                    fields['status'] + 
                  '</button>' +
                  '<form action="/processOrder/" method="post">' +
                    '<input type="hidden" name="location" value="'+ data.location + '">' +
                    '<input type="hidden" name="order" value="'+ pk_list[order] +'">' + 
                    '<div class="dropdown-menu" aria-labelledby="dropdownMenuButton2">' +
                    '<button class="dropdown-item" type="submit" name="status" value="Completed">Completed</button>' +
                    '</div></form></div></td></tr>';

            	html += text;
			}
		}

		$('#body').append(html)

		//update the hidden value
		$('#num').attr('value', num)
		for ( var order in new_order) {
			 var n = '<input type="hidden" class="pk" value="'+ new_order[order]+ '">';
			 $("body").append(n);
		}


	}

}