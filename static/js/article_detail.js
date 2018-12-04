$("#div_digg .action").click(function () {
    if ($(".info").attr("username")) {
        var is_up = $(this).hasClass("diggit");
        var article_id = $(".info").attr("article_id");

        $.ajax({
            url: "/blog/up_down/",
            type: "post",
            data: {
                is_up: is_up,
                article_id: article_id,
                csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val()
            },
            success: function (data) {
                if (data.status) {
                    if (is_up) {
                        var val = $("#digg_count").text();
                        val = parseInt(val) + 1;
                        $("#digg_count").text(val);
                    } else {
                        var val = $("#bury_count").text();
                        val = parseInt(val) + 1;
                        $("#bury_count").text(val);
                    }
                } else {
                    if (data.first_action) {
                        $("#digg_tips").text("您已经推荐过了");
                    } else {
                        $("#digg_tips").text("您已经反对过了");
                    }
                }
            }
        });
        setTimeout(function () {
            $("#digg_tips").text("");
        }, 1000)
    } else {
        location.href = "/login/";
    }
});

var pid = "";
$("#comment_btn").click(function () {
    var article_id = $(".info").attr("article_id");
    var content = $("#comment_content").val();
    var comment_count = $(".info").attr("comment_count");

    if (pid){
        var index = content.indexOf("\n");
        content = content.slice(index+1);
    }

    $.ajax({
        url: "/blog/comment/",
        type: "post",
        data: {
            article_id: article_id,
            content: content,
            pid: pid,
            comment_count: comment_count,
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val()
        },
        success: function (data) {
            var create_time = data.create_time;
            var content = data.content;
            var username = data.username;

            var comment_li = '<li class="list-group-item"> <span style="color: gray;">'+create_time+'</span> &nbsp;&nbsp; <a href=""><span>'+username+'</span></a><div class="con"> <p>'+content+'</p> </div> </li>';

            $(".comment_list").append(comment_li);

            // 清空文本框
            $("#comment_content").val("");
            pid = "";
        }
    });
});


$(".reply_btn").click(function () {
    $("#comment_content").focus();

    var v = "@" + $(this).attr("username") + "\n";
    $("#comment_content").val(v);

    pid = $(this).attr("comment_pk");
});

