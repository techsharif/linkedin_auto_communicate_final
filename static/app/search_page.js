ACCOUNT_SEARCH_URL = ''
$(document).ready(function () {
    console.log("ready!");


    function create_ajax_requst_data() {
        var ajax_request_data = new Object();
        ajax_request_data.search_text = '';
        ajax_request_data.search_head = '';
        ajax_request_data.page = '';
        ajax_request_data.order_by = '';

        return ajax_request_data;
    }

    $('#ajax_data_render_field').html(JSON.stringify(create_ajax_requst_data()));


    function load_data() {
        data = JSON.parse($('#ajax_data_render_field')[0].innerHTML)
        $.ajax({
            url: ACCOUNT_SEARCH_URL,
            type: "post",
            data: data,
            success: function (response) {
                $('#search_people').html(response);

            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
            }


        });
    }

    $(".search-item").click(function () {
        set_search_head($(this).context.firstElementChild.innerHTML);
        load_data();

        $(".search-item").removeClass('active');
        $(this).addClass('active');


    });


    function set_ajax_data(data) {
        $('#ajax_data_render_field').html(JSON.stringify(data));
    }

    function get_ajax_data() {
        data = JSON.parse($('#ajax_data_render_field')[0].innerHTML);
        return data;
    }

    function set_search_head(head) {
        data = get_ajax_data();
        data.search_head = head;
        set_ajax_data(data);
    }


    load_data();


    $("#new_search").click(function () {
        $('#add_search').modal('show');
    });






});