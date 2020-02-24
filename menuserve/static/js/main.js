

function add(event) {
    item_id = $(event).attr('value')
    order_id = $(event).next('.hidden').attr('value')
        //order_location = $(event).next('.hidden_location').attr('value')

        $.ajax({
            url: "/addToOrder/",
            type: "POST",
            data: { 'itemID': item_id, 'orderID': order_id},
            success: function(data)
            {
                addCart(data)

            }
        });
    }

function addCart(data) {

    var item = data.item;
    var pk = data.pk;
    var quantity = data.quantity;
    var order =data.order;
    var action = data.action;

    if (action == 'new') {

        html = '<li id="'+pk+'" class="list-group-item d-flex justify-content-between align-items-center pt-2 pb-2">' +
        item +' * 1'+
        '<button onclick="remove(this)" class="plusbutton">'+
        '<ion-icon name="close" class="close" ></ion-icon>'+
        '</button>'+
        '<input type="hidden" class="order_pk" value="'+ order +'">'+
        '<input type="hidden" class="item_pk" value="' + pk + '">'+
        '</li>'

        $("#orderlist").append(html)

    } else {

        var selector = '#'+ pk;
        var html = item + ' * ' + quantity +
        '<button onclick="remove(this)" class="plusbutton">'+
        '<ion-icon name="close" class="close" ></ion-icon>'+
        '</button>'+
        '<input type="hidden" class="order_pk" value="'+ order +'">'+
        '<input type="hidden" class="item_pk" value="' + pk + '">';
        $(selector).html(html)

    }

}

function remove(event) {

    item_id = $(event).siblings('.item_pk').attr('value')
    console.log(item_id)
    order_id = $(event).siblings('.order_pk').attr('value')

    $.ajax({
        url: "/removeFromOrder/",
        type: "POST",
        data: { 'itemID': item_id, 'orderID': order_id},
        success: function(data)
        {
            var pk = data.pk;
            var action = data.action;
            var name = data.name;
            var quantity = data.quantity;
            var order = data.order;

            var selector = '#'+ pk;

            if (action == 'remove') {

            $(selector).remove();

        } else {
            var selector = '#'+ pk;
            var html = name + ' * ' + quantity +
        '<button onclick="remove(this)" class="plusbutton">'+
        '<ion-icon name="close" class="close" ></ion-icon>'+
        '</button>'+
        '<input type="hidden" class="order_pk" value="'+ order +'">'+
        '<input type="hidden" class="item_pk" value="' + pk + '">';
            $(selector).html(html)

        }

        }
    });

}
