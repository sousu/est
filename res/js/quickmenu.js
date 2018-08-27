// Silver Pride Software Limited
// (c) 2008 - All rights reserved
// http://www.silver-pride.com
// Please note: This code is still under development.  Express permission must be
// obtained from Silver Pride Software before use.
// <reference path="jquery.intellisense.js"/>
//
//  内部でjScrollbar利用するため独自実装やスタイル関係のリテラルを含む

jQuery.fn.QuickMenu = function() {
    //-- init for recycle
    initId();

    $('ul.quickmenu-data li').addClass('quickmenuitem');
    $('ul.quickmenu-data li:has(ul)').addClass('quickmenuitem-haschildren');
    $('ul.quickmenu-data, ul.quickmenu-data ul').each(assigneachPaneId);
    $('ul.quickmenupane').each(addNavigationLinks);
    $('.quickmenuitem a').wrapInner('<div class="item"></div>')
    $('.quickmenuitem label').wrapInner('<div class="item"></div>')
    //--- Perfect-scroll ---
    //$('.quickmenupane').wrapInner('<div class="pscroll"></div>');
    //--- jScrollbar ---
    $('.quickmenupane').wrapInner('<div class="jScrollbar"><div class="jScrollbar_mask"></div></div>');
    $('.jScrollbar').append('<div class="jScrollbar_draggable"><a href="#" class="draggable"></a></div>');
    $('.jScrollbar').append('<div class="clr"></div>');
    // --- ---
    $('.quickmenupane').appendTo('#menuholder');
    $('#quickmenupane0').show();
    //--- Perfect-scroll ---
    //$('.pscroll').perfectScrollbar({
    //    suppressScrollX: true
    //});
    //--- jScrollbar ---
    h=$('.jScrollbar_mask').height();
    console.log(h);
    if(h<300){                  step = 28; }
    else if(h>=300  && h<1000){ step = 23; }
    else if(h>=1000 && h<3000){ step = 11; }
    else if(h>=3000 && h<6000){ step = 5;  }
    else {                      step = 3;  }
    $('.jScrollbar').jScrollbar({
        scrollStep : step
    });
}

function initId(){
    n=0;
    paneId=0;
}

function addNavigationLinks() {
    var parentPageId = $(this).attr('id');

    $(this).children('li:has(ul)').each(function() {
        var parentCallback = 'unshowPane(\'#' + parentPageId + '\', \'#' + $(this).children('ul:first').attr('id') + '\')';
        var parentName = $(this).children('label:first').text();
        //var parentName = $(this).children('a:first').text();
        var linkId = parentPageId + '_link';
        $(this).children('ul').prepend('<div onclick="'+parentCallback+'" class="parentLink" >'+parentName+'</div>');
    });
}

function assigneachItem() {
    this.id = 'quickmenuitem' + n++;
}

function assigneachPaneId() {
    var newId = 'quickmenupane' + paneId++;
    this.id = newId;


    $(this).addClass('quickmenupane');
    $(this).css('display', 'none');
    var callback = 'showPane(\'#' + newId + '\');';

    // Add display event handler to parent item
    var linkId = newId + '_link';
    $(this).parent().append('<div class="showchild" id="' + linkId + '" >&nbsp;</div>');
    $('#' + linkId).click(function(){ 
        eval(callback);
    });
}

function debugeach() {
    alert(this.innerText + " id = " + this.id);
}

function showPane(paneId) {
    $(paneId).fadeIn();
    //--- jScrollbar ---
    $('.jScrollbar').jScrollbar({
        scrollStep : step
    });

}

function unshowPane(paneId, unshowpaneId) {
    // Fly old menu out to right
    $(unshowpaneId).fadeOut(200);
    $(paneId).fadeIn(200);        
}

