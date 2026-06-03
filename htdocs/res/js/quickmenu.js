// Silver Pride Software Limited
// (c) 2008 - All rights reserved
// http://www.silver-pride.com
// Please note: This code is still under development.  Express permission must be
// obtained from Silver Pride Software before use.
// <reference path="jquery.intellisense.js"/>
//
//  スクロールはネイティブ(.quickmenupane overflow:auto)に変更済

jQuery.fn.QuickMenu = function() {
    //-- init for recycle
    initId();

    $('ul.quickmenu-data li').addClass('quickmenuitem');
    $('ul.quickmenu-data li:has(ul)').addClass('quickmenuitem-haschildren');
    $('ul.quickmenu-data, ul.quickmenu-data ul').each(assigneachPaneId);
    $('ul.quickmenupane').each(addNavigationLinks);
    $('.quickmenuitem a').wrapInner('<div class="item"></div>')
    $('.quickmenuitem label').wrapInner('<div class="item"></div>')
    //--- native scroll (.quickmenupane の overflow:auto を利用) ---
    $('.quickmenupane').appendTo('#menuholder');
    //--- スクロール中だけバー表示(オートハイド) ---
    $('.quickmenupane').on('scroll', function(){
        var p=$(this); p.addClass('scrolling');
        clearTimeout(p.data('st'));
        p.data('st', setTimeout(function(){ p.removeClass('scrolling'); }, 700));
    });
    $('#quickmenupane0').show();
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
}

function unshowPane(paneId, unshowpaneId) {
    // Fly old menu out to right
    $(unshowpaneId).fadeOut(50);
    $(paneId).fadeIn(50);        
}

