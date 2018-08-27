
// est_client.js

if (!('console' in window)) { // for IE
    window.console = {};
    window.console.log = function(str){return;};
    window.console.debug = function(str){return;};
};

jQuery(function($){
    $.ajaxSetup({ cache: false }); 
    
    var parts = "casket_publish/parts/";
    var cur_genre_id = "";
    var cur_root = "";
    var estinfo = "";
    var selected_dirs = [];
    var refer_roots = [];

    // --- est info ---
    $('div#estinfo').text(function(index,txt){
        var m = txt.match(/with ([0-9]+) documents and ([0-9]+)/);
        estinfo = m[1]+"文書 / "+m[2]+"単語";
        return "　";
    });
    // --- logo ---
    $("a.sikumi").click(function () {
        $("#sikumi").toggle();
        $("div.logo").toggleClass("chink");
    });
    // --- genre load ---
    $('div.genres').load(parts+'genre',function(){
        cur_genre_id = ($.cookie('est_selected_genre'))? 
            $.cookie('est_selected_genre') : $('.genre_link:first',$(this)).attr('id');
        // info
        $('div#estinfo').text(function(index,txt){
            $.ajaxSetup({ async: false });
            //var pre = "最終更新 ["+$('#'+cur_genre_id).text()+"]: "
            var pre = "最終更新: "
            $.get(parts+'ts_'+cur_genre_id+'.json',function(data){
                pre = pre+data['ts'];
            });
            $.ajaxSetup({ async: true });
            return pre+" | 全体 "+estinfo;
        });
        $('ul.roots').load(parts+cur_genre_id+'_'+'entry_roots',function(){
            set_root(this);
            $('#scroll').smoothDivScroll({
                mouseDownSpeedBooster: 2
            });

            $('span.pop_button.normal').click(function(){
                qm_remove(); 
                root_num = $(this).attr('id');
                cur_root = 'd'+root_num.match(/\d+/);
                $('#pop_menu').load(parts+cur_genre_id+'_'+root_num, function(){
                    $('ul.quickmenu-data').QuickMenu();
                    set_dir($('.quickmenu'));
                });
                qm_shift($(this).offset().left);
                $('.quickmenu').slideDown();
                $(this).addClass('down'); 
            });
            for(var i=0; i<selected_dirs.length; i++){
                $('input#'+selected_dirs[i]).attr("checked",true);
                root_check($('input#'+selected_dirs[i]));
            };
        });
        $('#'+cur_genre_id, $(this)).addClass('selected');
        $('.genre_link', $(this)).click(function(){
            $.cookie('est_selected_genre', $(this).attr('id')); 
            $.cookie('est_selected_dirs', null); 
            $.cookie('est_refer_roots', null); 
        });
    });
    selected_dirs = ($.cookie('est_selected_dirs'))? 
        $.cookie('est_selected_dirs').split(':') : [];
    refer_roots = ($.cookie('est_refer_roots'))? 
        $.cookie('est_refer_roots').split(':') : [];

    //  --- quickmenu ---
    function qm_remove(){
        $('.quickmenu').hide();
        $('#pop_menu').empty(); // 管理用divの空白化
        $('#menuholder').empty(); // 実データ用divの空白化
        $('span.pop_button').removeClass('down');
        cur_root = "";
    };
    function qm_shift(left_offset){
        var margin = $('#main').offset().left + 10; // XXpxは中心寄せの評価値
        var shift_val = left_offset - margin;
        var width = $('#main').width();
        var size = $('.quickmenu').width();
        if(shift_val+size > width)  // 右端を超える場合
            shift_val = width-size - 2; // 右端に揃える 2pxはboder分
        $('.quickmenu').css({ left:shift_val });
    };
    // Root
    function set_root(roots){
        for(var i=0; i<refer_roots.length; i++)
            root_refer(refer_roots[i]);
        $('input.dir',$(roots)).change(function(){
            if($(this).is(':checked')){
                push_dir($(this).attr('id'));
                root_check(this);
                qm_close_check($(this).attr('id'));
            }else{
                del_dir($(this).attr('id'));
                root_uncheck(this);
            };
        });
    };
    function closest_label(input){
        return $(input).closest('label');
    };
    function root_check(elem){
        $(closest_label(elem)).addClass('checked');
        $(closest_label(elem)).next().removeClass('normal');
        $(closest_label(elem)).next().addClass('void');
    };
    function root_uncheck(elem){
        $(closest_label(elem)).removeClass('checked');
        $(closest_label(elem)).next().addClass('normal');
        $(closest_label(elem)).next().removeClass('void');
    };
    function qm_close_check(id){
        if(id == cur_root) qm_remove();
    };
    // Dir
    function set_dir(qm){
        dir_reflesh(qm);

        $('input.dir',$(qm)).change(function(){
            if($(this).is(':checked')){
                push_dir($(this).attr('id'));
                root_refer(cur_root);
                push_refer(cur_root);
            }else{
                del_dir($(this).attr('id'));
                if($(qm).find('input:checked').length == 0){
                    root_unrefer(cur_root);
                    del_refer(cur_root);
                };
            };
            dir_reflesh(qm);
        });
    };
    function dir_reflesh(qm){
        // Check付け外しの度に全体を走査
        clear_qm(qm); 
        for(var i=0; i<selected_dirs.length; i++){
            var input = $('input#'+selected_dirs[i]);
            $(input).attr("checked",true);
            qm_check(input); 
            qm_refer(input, qm);
        };
    };
    //!issue 全般的にQuickMenuの構造に依存
    function clear_qm(range){
        $('label.'+'checked',$(range)).removeClass('checked');
        $('label.'+'referrd',$(range)).removeClass('referrd');
        $('div.'+'void',$(range)).removeClass('void');
    };
    function qm_check(elem){
        $(closest_label(elem)).addClass('checked');
        $(closest_label(elem)).next().addClass('void');
    };
    function qm_refer(elem, range){
        var pane_id = $(elem).closest('.quickmenupane').attr('id');
        var near_div = $('#'+pane_id+'_link',$(range));
        if(!near_div.length) return;
        var target_input = $(near_div).closest('li').find('input');
        $(closest_label(target_input)).addClass('referrd');
        qm_refer(target_input,range); // 上位パネルを再帰的に確認
    };
    function root_refer(root){
        $(closest_label($('input#'+root,$('ul.roots')))).addClass('referrd');
    };
    function root_unrefer(root){
        $(closest_label($('input#'+root,$('ul.roots')))).removeClass('referrd');
    };
    // in out
    function push_dir(dir){
        for(var i=0; i<selected_dirs.length; i++)
            if (selected_dirs[i] == dir) return;
        selected_dirs.push(dir);
        console.debug("push: "+selected_dirs);
    };
    function del_dir(dir){
        for(var i=0; i<selected_dirs.length; i++)
            if (selected_dirs[i] == dir) selected_dirs.splice(i--, 1);
        console.debug("del: "+selected_dirs);
    };
    //!issue 共通化
    function push_refer(root){
        for(var i=0; i<refer_roots.length; i++)
            if (refer_roots[i] == root) return;
        refer_roots.push(cur_root);
    };
    function del_refer(root){
        for(var i=0; i<refer_roots.length; i++)
            if (refer_roots[i] == root) refer_roots.splice(i--, 1);
    };

    // --- mdate ---
    $('.doc_val_mdate').text(function(index,txt){
        txt = txt.replace(/([0-9]{4})-0?([0-9]+)-0?([0-9]+)T0?([0-9]+):0?([0-9]+):0?([0-9]+)Z/,"$1/$2/$3 $4:$5:$6 +0000");
        var date = new Date(txt);
        var y = date.getFullYear().toString();
        var m = date.getMonth()+1;
        var d = date.getDate();
        var hour = date.getHours();
        var min = date.getMinutes();
        if(m < 10) m = '0' + m.toString(); 
        if(d < 10) d = '0' + d.toString(); 
        if(hour < 10) hour = '0' +hour.toString(); 
        if(min < 10) min = '0' +min.toString();
        return y+"/"+m+"/"+d+" "+hour+":"+min;
    });

    // --- size ---
    $('.doc_val_size').text(function(index, v){
        if(v > 1000000){      return (Math.round(v/100000)/10)+" MB";
        } else if(v > 10000){ return Math.round(v/1000)+" KB";
        } else if(v > 100){   return (Math.round(v/100)/10)+" KB";
        } else {              return v+" B";
        }; 
    });

    // --- order ---
    var order = ($.cookie('est_order'))? 
        $.cookie('est_order') : "score";
    $('#submittool a#'+order+' img').addClass('selected-order');
    $('#submittool a.order').click(function(){
        order = $(this).attr('id');
        $.cookie('est_order', order); 
        $('#submittool a.order img').removeClass('selected-order');
        $('img',this).addClass('selected-order');
    });
    $('#submittool a.selected-order').click(function(e){
        return false;
    });

    // --- copy ---
    if(('Clipboard' in window)){
        $('dd.doc_navi').each(function(){
            var s = $(this).children('.dir').attr('href');
            $(this).append('<a class="copy" href="javascript:void(0)" data-clipboard-text="'+s+'">[copy]</a>');
        });
       new Clipboard('.copy');
    }

    // --- submit ---
    $('a.submitter').click(function(){
        $('form#form_self').submit();
    });
    est_submit = function(){  // Global関数として設定
        //選択Dirの保存
        $.cookie('est_selected_dirs', selected_dirs.join(':')); 
        $.cookie('est_refer_roots', refer_roots.join(':')); 

        $.ajaxSetup({ async: false }); // Submitが発行されてしまうので同期通信化
        var q = ''
        $.getJSON(parts+cur_genre_id+'_'+'ids.json', function(data){
            for(var i=0;i<selected_dirs.length; i++){
                q = q +"|"+ data[selected_dirs[i]];
            };
        });
        $.ajaxSetup({ async: true });
        if(q==''){ q='@genre STREQ '+cur_genre_id;
        } else {   q='@root,@dep1,@dep2,@dep3,@dep4,@dep5 STRRX '+q.substr(1);
        }

        $('select#perpage').val('20');
        $('input#attr').val(q); 
        switch(order) {
            case "date": $('input#order').val('@mdate NUMD'); break;
            default: $('input#order').val(''); break;
        }
    };

    // --- similer ---
    if(/^\[SIMILAR\]/.test($('input#phrase').val())) $('input#phrase').val('');
    $('a.similar').click(function(){
        var url = $(this).attr('href');
        url = url+'&attr=@genre+STREQ+'+cur_genre_id;
        $.cookie('est_selected_dirs', null); 
        $.cookie('est_refer_roots', null); 
        switch(order) {
            case "date": url = url+"&order=@mdate+NUMD" ; break;
            default: break;
        }
        $(this).attr('href',url);
    });
});

