var _search='';
var _categories=[];
var _laypage;
var _laypage_config={
    elem: 'divlaypage' //注意，这里的 test1 是 ID，不用加 # 号
    , count: 0
    , limit: 5
    , limits: [10, 15, 20, 25, 50]
    , jump: function (obj, first) {
        getListData(obj.curr, obj.limit);
    }
}

layui.use('laypage', function () {
    _laypage = layui.laypage;
});
layui.use('form', function () {
    var form = layui.form;
    //监听查询
    form.on('submit(query)', function (data) {
        _categories = [];
        $.each(data.field, function(key){
            if(key == "search"){
                _search = data.field[key]
            }else if(data.field[key] == 'on'){
                _categories.push('\''+key + '\'');
            }
        });
        getListCount();
        return false;
    });
    $('#btnreset').bind('click',function(){
        _categories=[];
        _search='';
    })
});
$(document).ready(function () {
    $('span.category').hover(function () {
        $(this).next().css('backgorund-color', '#e25050');
    }, function () {
        $(this).next().css('backgorund-color', '#393939');
    });
    $('#search').val($('#search_index').val())
    getcategories();
});

// 获取列表的数量
function getListCount(){
    $.getJSON($SCRIPT_ROOT + "/getlistcount",
        {search:_search, categories:_categories.join(",")},
        function (data) {
            _laypage_config.count = data;
            _laypage.render(_laypage_config);
        }
    )
}

// 获取列表数据
function getListData(pageIndex, limit) {
    $.getJSON($SCRIPT_ROOT + "/getlistdata",
        {pageIndex:pageIndex, limit:limit},
        function (data) {
            var ul_html = '<ul class="pageing">'
            $.each(data.items, function (i) {
                ul_html += `
                <li>
                    <div class="post">
                        <h1 class="title">
                            <a href="detail/${data.items[i]["id"]}" target="_blank">
                                ${data.items[i]["question"]}
                            </a>
                        </h1>
                        <div class="meta">
                            <ul>
                                <li class="category"><a href="#">${data.items[i]["category"]}</a></li>    
                                <li class="admin"><a href="#">${data.items[i]["admin"]}</a></li>
                                <li class="date">${data.items[i]["date"]}</li>
                                <li class="comments"><a href="#">Clicked ${data.items[i]["clicks"]} Times</a></li>
                            </ul>
                        </div>
                        <!--end meta-->

                        <span class="main-border"></span>

                        <p>
                            <a href="{{ url_for('qa_blue.detail', id=${data.items[i]['id']}) }}" target="_blank">
                                ${data.items[i]["answer"].slice(0,100)}......
                            </a>
                        </p>
                        <div class="clear"></div>
                    </div>
                    <!--END post-->
                </li>`;
            })

            ul_html += '</ul><div class="Pagination"></div><div class="clear"></div>';


            $("#main-content").html(ul_html);
        }
    )

}

// 获取问题类型数据
function getcategories() {
    $.getJSON($SCRIPT_ROOT + "/getcategories",
        function (data) {
            var ul_html = ''
            $.each(data.items, function (i) {
                ul_html += `
                <li>
                    <input type="checkbox" name="${data.items[i].id}" title="${data.items[i].category}" lay-skin="primary" checked>
                </li>`;
            });

            $("#ulcategories").html(ul_html);
            getListCount();
        }
    )
}