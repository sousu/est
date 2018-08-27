/************************************************************************
@Name: jScrollbar - jQuery Plugin
@Revison: 1.0
@Date: 21/03/2011
@Author: ALPIXEL - http://www.myjqueryplugins.com - http://www.alpixel.fr
@License: Open Source - MIT License : http://www.opensource.org/licenses/mit-license.php
**************************************************************************/
// 表示非表示関係等の独自実装を含む

(function($) {
	$.fn.jScrollbar= function(op) {
        var defaults = {
			scrollStep : 15,
			allowMouseWheel : true
        };
		
        if(this.length>0)
	    return this.each(function() {

			var 
				$this = $(this),
				opts = $.extend(defaults, op),
				js_mask = $this.find('.jScrollbar_mask'), /* 動かし対象 */
				js_drag = $this.find('.jScrollbar_draggable a.draggable'), /* Bar */
				js_Parentdrag = $this.find('.jScrollbar_draggable'),
				diff = parseInt(js_mask.innerHeight()) - parseInt($this.height());
			
			/** if mask container is heighter than the main container **/
			if(diff > 0){
				js_Parentdrag.show();
				var pxDraggable = parseInt(js_Parentdrag.height()) - parseInt(js_drag.height());;
				var pxUpWhenScrollMove = opts.scrollStep;
				var pxUpWhenMaskMove = pxUpWhenScrollMove * (diff/pxDraggable);

                // 超えている場合のみ表示
				js_drag.show();

                /** drag **/ 
				js_drag
				.click(function(e){e.preventDefault();})
				.draggable({
					axis:'y',
					containment: js_Parentdrag,
					scroll: false,
					drag: function(event, ui){
						js_mask.css('top','-'+(ui.position.top * (diff/pxDraggable))+'px');
					}
				});
				
				/** if mousewheel allowed **/
				if(opts.allowMouseWheel){
                    // 異常加速を防ぐため一度消す
                    $this.unbind("mousewheel"); 

                    $this.mousewheel(function(objEvent, intDelta) {
                        //console.log(intDelta);
                        // mousewheel up (first if)  and mousewheel down (second if)
                        if (intDelta > 0 && parseInt(js_mask.css('top')) < 0){
                            js_drag.stop(true, true).animate({top:'-='+pxUpWhenScrollMove+'px'},10);
                            js_mask.stop(true, true).animate({top:'+='+pxUpWhenMaskMove+'px'},10,function(){
                                RelativeTop = parseInt(js_mask.css('top'));
                                if(RelativeTop > -3 ) {
                                    js_drag.css({top:0});
                                    js_mask.css({top:0});
                                }
                            });
                        }
                        else if (intDelta < 00 && parseInt(js_mask.css('top')) > -diff) {
                            js_drag.stop(true, true).animate({top:'+='+pxUpWhenScrollMove+'px'}, 10);
                            js_mask.stop(true, true).animate({top:'-='+pxUpWhenMaskMove+'px'},10,function(){
                                RelativeTop = parseInt(js_mask.css('top'));
                                if(RelativeTop < -diff+3)
                                {
                                    js_mask.css({top:-diff});
                                    js_drag.css({top:pxDraggable});
                                }
                            });
                        }
                        // ブラウザのスクロールイベントを伝達させない
                        objEvent.stopPropagation();
                        objEvent.preventDefault();
                    });
                }
			} else {
                // 超えない場合は表示しない
				js_drag.hide();
            }
		});
	}
})(jQuery);

