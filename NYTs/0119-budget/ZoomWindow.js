var NYTG = NYTG || {};
NYTG.csstransitions = Modernizr.csstransitions;
//requires jQuery
//requires jQuery mouseWheel plugin.

NYTG.ZoomWindow = function (nodeId, treeMap) {
    
    this.HOUSEHOLDS = 113616229;
    
    this.j = jQuery;
    this.window = document;
    //TODO window
    
    this.frameSize = {};
    this.frameSize.width = 0;
    this.frameSize.height = 0;
    this.frameSize.x = 0;
    this.frameSize.y = 0;
    this.pageWidth = 0;
    this.pageHeight = 0;
    
    
    this.zoomLevel = 1;
    this.zoomStep = 2;
    this.minZoomLevel = 1;
    this.maxZoomLevel = 64;
    
    this.gestureStartScale;
    this.mouseMoveCallback = function() {};
    
    this.treeMap = treeMap;
    
    this.currentHighlightedNode = -1;
    this.currentAnnotatedNode = -1;
    
    // this.zoomCenter = {};
    // this.zoomCenter.x = 0.50; //note this is represented by a fraction (0-1) of the frame size
    // this.zoomCenter.y = 0.50; //note this is represented by a fraction (0-1) of the frame size
    
    this.center = {};
    this.center.x = 0.50; //note this is represented by a fraction (0-1) of the content size
    this.center.y = 0.50; //note this is represented by a fraction (0-1) of the content size
    
    this.dragDelta = {};
    this.dragDelta.x = 0;
    this.dragDelta.y = 0;
    
    this.clickStart = {};
    this.clickStart.x = 0;
    this.clickStart.y = 0;
    this.dragStart = {};
    this.dragStart.x = 0; //in pixels
    this.dragStart.y = 0; //in pixels
    this.isDragging = false;
    
    this.cssUpdates = {};
        
    this.container = this.j("#" + nodeId);
    this.dragContainer = this.container.wrap(this.j("<div class='nytg-dragContainer'></div>")).parent();
    this.zoomContainer = this.dragContainer.wrap(this.j("<div class='nytg-zoomContainer'></div>")).parent();
    this.pinchContainer = this.zoomContainer.wrap(this.j("<div class='nytg-pinchContainer'></div>")).parent();
    this.zoomFrame = this.pinchContainer.wrap(this.j("<div class='nytg-zoomFrame'></div>")).parent();
    this.zoomOverlay = this.zoomFrame.before(this.j("<div class='nytg-zoomOverlay'></div>")).prev();
    //<img src='http://graphics8.nytimes.com/images/spacer.gif' />
    
    this.highlightBox = this.j("<div class='nytg-zoomContainer-highlightBox'><div></div></div>");
    this.dragContainer.append(this.highlightBox);
    
    this.annotateBox = this.j("<div class='nytg-zoomContainer-annotateBox'><div></div></div>");
    this.dragContainer.append(this.annotateBox);
    
    this.infoPane = this.j("<div class='nytg-zoomContainer-infoPane' style='display:none'></div>");
    this.j('#nytg-wrapper').append(this.infoPane);
    
    this.init();
        
};

//----------------------------------------------
// CONSTRUCTOR
//----------------------------------------------

NYTG.ZoomWindow.prototype.init = function() {
    // this.zoomContainer = this.container.find(".nytg-zoomContainer").first();
    // this.dragContainer = this.container.find(".nytg-dragContainer").first();
    // this.pinchContainer = this.container.find(".nytg-pinchContainer").first();
    // this.zoomOverlay = this.container.find(".nytg-zoomOverlay").first();
    // this.zoomFrame = this.container.find("nytg-zoomFrame").first();
    this.highlightBox.hide();
    this.annotateBox.hide();
    this.zoomContainer.css({
        position:"absolute",
        left: 0,
        top: 0,
        width:"100%",
        height: "100%"
    });
    this.pinchContainer.css({
        position:"absolute",
        left: 0,
        top: 0,
        width:"100%",
        height: "100%"
    });
    this.dragContainer.css({
        position:"absolute",
        width:"100%",
        height: "100%"
    });
    this.zoomFrame.css({
        position:"absolute",
        width:"100%",
        height:"100%",
        overflow:"hidden"
    });
    this.highlightBox.css({
        position:"absolute",
        left:0,
        top:0,
        "z-index":1000
    });
    this.annotateBox.css({
        position:"absolute",
        left:0,
        top:0,
        "z-index":999});
    this.infoPane.css({
        position:"absolute",
        left: -200,
        top: -200,
        "z-index":1000
    });
        
    this.initEvents();
    this.resize();
};


//----------------------------------------------
// EVENTS
//----------------------------------------------

NYTG.ZoomWindow.prototype.initEvents = function() {
    var me = this;
    
    //Mouse wheel zooming.
    this.zoomFrame.bind('mousewheel', function(evt, delta, deltaX, deltaY){
        var zoomFactor,
            zoomX,zoomY,
            zoomDirection,
            zoomAmount;
            
        
        if (isNaN(evt.wheelDelta)) {
            evt.wheelDelta = delta * 1000
        };
        
        if (evt.wheelDelta > 0) {
            zoomDirection = true;
        } else {
            zoomDirection = false;
        }
        zoomAmount = Math.abs(evt.wheelDelta);
        
        zoomAmount = Math.min(zoomAmount, 6000);
        zoomAmount = Math.max(zoomAmount, 0)
        
        if (zoomDirection) {
            zoomFactor = 1 + zoomAmount / 8000;
        } else {
            zoomFactor = 1 / ( 1 + zoomAmount / 8000 ) ;
        }
        
        // console.log("zf:"+zoomFactor);
        pixelsFromOriginX = evt.pageX - me.frameSize.x;
        pixelsFromCenterX = pixelsFromOriginX - me.frameSize.width / 2;
        ratioFromOriginX = pixelsFromOriginX / me.frameSize.width;
        ratioFromCenterX = pixelsFromCenterX / me.frameSize.width;
        
        pixelsFromOriginY = evt.pageY - me.frameSize.y;
        pixelsFromCenterY = pixelsFromOriginY - me.frameSize.height / 2;
        ratioFromOriginY = pixelsFromOriginY / me.frameSize.height;
        ratioFromCenterY = pixelsFromCenterY / me.frameSize.height;
        
        zoomX = me.center.x + ( ratioFromCenterX / me.zoomLevel ) - ( ratioFromCenterX / me.zoomLevel ) / ( zoomFactor );
        zoomY = me.center.y + ( ratioFromCenterY / me.zoomLevel ) - ( ratioFromCenterY / me.zoomLevel ) / ( zoomFactor );
        
        
        me.zoom(zoomFactor, false);
        
        //pct offset
        
        // console.log(zoomX +":" +zoomY)
        
        me.updateCenter(zoomX, zoomY);
        me.renderCycle(false)
        
    }, false);
    
    this.zoomOverlay.hide();
    
    // this.highlightBox.dblclick(function(evt){
    //     me.zoomToNode(me.currentHighlightedNode);
    // });
    
    this.annotateBox.bind('mouseover', function(evt) {
        // console.log(me.currentAnnotatedNode);
        if (!me.isDragging) {
            me.infoPane.show();
            me.highlightBox.show();
            me.highlightNode(me.currentAnnotatedNode);
        };
        // this.currentAnnotatedNode
    })
    
    
    // this.j('.treeMap-leaf').live('dblclick', function(evt) {
    //   me.zoomToNode(evt.currentTarget.id);
    // });
    // this.j('.label-heading').live('click', function(evt) {
    //   me.highlightNode(me.j(evt.currentTarget).parent().parent()[0].id);
    // });
    
    this.zoomFrame.bind('mouseover', function(evt) {
        if (!me.isDragging) {
            me.infoPane.show();
            me.highlightBox.show();
            me.zoomFrame.bind('mousemove', function(evt){
                me.mouseMoveHandler(evt);
            });
        }
    });
    
    this.zoomFrame.bind('mouseout', function(evt) {
        me.infoPane.hide();
        me.highlightBox.hide();
        me.zoomFrame.unbind('mousemove');
    });
    
    this.j('.treeMap-leaf').live('mouseover', function(evt) {
        // console.log(evt.currentTarget.id);
        if (!me.isDragging) {
            me.infoPane.show();
            me.highlightBox.show();
            me.highlightNode(evt.currentTarget.id);
        };
    });
    
    //Gesture events
    // this.zoomFrame.bind("gesturestart", function(evt) { me.gestureStartHandler(evt) }, false);
    // this.zoomOverlay[0].addEventListener("gesturechange", function(evt) { me.gestureChangeHandler(evt) }, false);
    // this.zoomOverlay[0].addEventListener("gestureend", function(evt) { me.gestureEndHandler(evt) }, false);
    this.zoomFrame.bind("touchstart", function(evt) { me.touchStartHandler(evt) }, false);
    
    
    
    //Dragging
    this.zoomFrame.bind( 'mousedown', function(evt){ me.startDrag(evt); }, false );

};


//gestures
NYTG.ZoomWindow.prototype.gestureStartHandler = function(evt) {
    var me = this;
    this.resize();
    evt.preventDefault();
    console.log("gesture start");
    this.isDragging = false;
    this.zoomFrame.bind("gesturechange", function(evt) { me.gestureChangeHandler(evt) }, false);
    this.zoomFrame.bind("gestureend", function(evt) { me.gestureEndHandler(evt) }, false);
};
NYTG.ZoomWindow.prototype.gestureChangeHandler = function(evt) {
    var me = this,
        xpct, ypct;
    
    evt.preventDefault();
    evt = evt.originalEvent;
    console.log(evt.scale);
    xpct = 0//-1*(this.center.x * this.zoomLevel*(evt.scale) - 0.5);
    ypct = 0//-1*(this.center.y * this.zoomLevel*(evt.scale) - 0.5);
    this.dragContainer.css({"-webkit-transform":"scale("+evt.scale+")"});
    // this.zoom(evt.scale, false);
    
};
NYTG.ZoomWindow.prototype.gestureEndHandler = function(evt) {
    var me = this;
    evt.preventDefault();
    evt = evt.originalEvent;
    this.dragContainer.css({"-webkit-transform":"none"});
    this.zoom(evt.scale, false);
    // console.log("gestureEnd")
    this.zoomFrame.unbind("gesturechange");
    this.zoomFrame.unbind("gestureend");
};

//touch
NYTG.ZoomWindow.prototype.touchStartHandler = function(evt) {
    var me = this;
    this.resize();
    evt.preventDefault();
    evt = evt.originalEvent;
    this.resize();
    if (evt.targetTouches.length != 1)
            return false;
    // console.log("touch start")
    this.zoomFrame.bind("touchmove", function(evt) { me.touchMoveHandler(evt) }, false);
    this.zoomFrame.bind("touchend", function(evt) { me.touchEndHandler(evt) }, false);
    this.isDragging = true;
    this.dragStart.x = evt.targetTouches[0].clientX;
    this.dragStart.y = evt.targetTouches[0].clientY;
    
    
};
NYTG.ZoomWindow.prototype.touchMoveHandler = function(evt) {
    evt.preventDefault();
    evt = evt.originalEvent;
    if (evt.targetTouches.length != 1)
            return false;

    this.dragDelta.x = evt.targetTouches[0].clientX - this.dragStart.x;
    this.dragDelta.y = evt.targetTouches[0].clientY - this.dragStart.y;
    
    // console.log(evt)
    this.dragContainer.css({
        "left": this.dragDelta.x + "px",
        "top": this.dragDelta.y + "px"
    });
};
NYTG.ZoomWindow.prototype.touchEndHandler = function(evt) {
    var hratio, vratio,
        me;
        
    me = this;
    
    evt.preventDefault();
    evt = evt.originalEvent;
    if (evt.targetTouches.length > 0)
            return false;
    
    this.zoomFrame.unbind('touchmove');
    this.zoomFrame.unbind('touchend');
    
    if (this.isDragging) {
        // console.log("touch end");
        this.dragContainer.css({
            "left": 0,
            "top": 0
        });

        // this.zoomContainer.removeClass("nytg-zoomAnimate");
        hratio = this.dragDelta.x / ( this.frameSize.width * this.zoomLevel );
        vratio = this.dragDelta.y / ( this.frameSize.height * this.zoomLevel );

        this.updateCenter(this.center.x - hratio, this.center.y - vratio);
        this.renderCycle(false);

        this.isDragging = false;
    };
    
};


//mousemove
NYTG.ZoomWindow.prototype.mouseMoveHandler = function(evt) {
    // console.log(evt);
    var x,y,w,h,
        lp, tp;
    
    lp = -45;
    tp = 45
    
    w = 300;
    h = 100;
    
    // w = this.infoPane.width();
    // h = this.infoPane.height();
    x = evt.pageX;
    y = evt.pageY;
    if ((x + w + lp + 100) > this.pageWidth) {
        lp = -250;
    };
    if ( ( y + h + tp + 100 ) > this.pageHeight ) {
        tp = - 140;
    };
    

    this.infoPane.css({
        left:x + lp ,
        top:y + tp
    })
};

//dragging
NYTG.ZoomWindow.prototype.startDrag = function ( evt ) {
    var me = this;
    // this.zoomContainer.removeClass("nytg-zoomAnimate");
    // console.log('start drag');
    this.isDragging = true;
    this.infoPane.hide();
    this.highlightBox.hide();
    this.resize();
    this.j(me.window).bind('mouseup', function(evt){ me.stopDrag(evt); });
    this.j(me.window).bind('mousemove', function(evt){ me.dragUpdate(evt); });
    this.dragStart.x = evt.pageX;
    this.clickStart.x = this.dragStart.x;
    this.dragStart.y = evt.pageY;
    this.clickStart.y = this.dragStart.y;
};
NYTG.ZoomWindow.prototype.dragUpdate = function ( evt ) {
    
    this.dragDelta.x = evt.pageX - this.dragStart.x;
    this.dragDelta.y = evt.pageY - this.dragStart.y;
    // this.dragContainer.css({
    //     "left": this.dragDelta.x + "px",
    //     "top": this.dragDelta.y + "px"
    // });
    hratio = this.dragDelta.x / ( this.frameSize.width * this.zoomLevel );
    vratio = this.dragDelta.y / ( this.frameSize.height * this.zoomLevel );
    this.updateCenter(this.center.x - hratio, this.center.y - vratio);
    this.renderCycle(false);
    this.dragStart.x = evt.pageX;
    this.dragStart.y = evt.pageY;
    
};
NYTG.ZoomWindow.prototype.stopDrag = function ( evt ) {
    var hratio,
        vratio;
    
    
    this.j( this.window ).unbind('mousemove');
    this.j( this.window ).unbind('mouseup');
    
    
    
    
    if (this.isDragging) {
        this.isDragging = false;
        //reset positions
        
        
        
        this.dragContainer.css({
            "left": 0,
            "top": 0
        });

        // this.zoomContainer.removeClass("nytg-zoomAnimate");
        hratio = this.dragDelta.x / ( this.frameSize.width * this.zoomLevel );
        vratio = this.dragDelta.y / ( this.frameSize.height * this.zoomLevel );

        this.updateCenter(this.center.x - hratio, this.center.y - vratio);
        this.renderCycle(false);
        if ((Math.abs(this.dragStart.x - this.clickStart.x) < 1)&&(Math.abs(this.dragStart.y - this.clickStart.y) < 1)) {
            this.zoomToNode(this.currentHighlightedNode);
        };
    };
    
    

    
    
};
//----------------------------------------------
// HIGHLIGHTING
//----------------------------------------------

NYTG.ZoomWindow.prototype.highlightNode = function(id) {
    var x,y,w,h,t,d;
    
    this.currentHighlightedNode = id;
    
    d = this.treeMap.findFromId(id);
    // console.log(d)
    
    this.j("#"+d['pid']+" .treeMap-branchContainer").first().prepend(this.highlightBox);
    
    t = this.treeMap.getBoundingBox(id);
    
    // this.zoomToBox(t.x1,t.y1,t.x2,t.y2, 0.7);
    
    // p = NYTG.z.projectFromFrameToContainer(evt.offsetX, evt.offsetY);
    x = 100*t.x1;
    y = 100*t.y1;
    w = 100*(t.x2 - t.x1)
    h = 100*(t.y2 - t.y1)
    
    this.highlightBox.css({
        left: d.cx + "%",
        top: d.cy + "%",
        width: d.cw + "%",
        height: d.ch + "%"
    });
    this.highlightBox.show();
    this.showInfoPane(id);
};

NYTG.ZoomWindow.prototype.annotateNode = function(id) {
    var x,y,w,h,t,d;
    
    // console.log("annotate");
    
    this.currentAnnotatedNode = id;
    
    d = this.treeMap.findFromId(id);
    // console.log(d)
    
    this.j("#"+d['pid']+" .treeMap-branchContainer").first().prepend(this.annotateBox);
    
    t = this.treeMap.getBoundingBox(id);
    
    this.zoomToNode(id);
    
    // p = NYTG.z.projectFromFrameToContainer(evt.offsetX, evt.offsetY);
    x = 100*t.x1;
    y = 100*t.y1;
    w = 100*(t.x2 - t.x1)
    h = 100*(t.y2 - t.y1)
    
    this.annotateBox.css({
        left: d.cx + "%",
        top: d.cy + "%",
        width: d.cw + "%",
        height: d.ch + "%"
    });
    this.annotateBox.show();
};

NYTG.ZoomWindow.prototype.zoomToNode = function(id) {
    // this.zoomContainer.addClass("nytg-zoomAnimate");
    // p = this.treeMap.findFromId(id).pid;
    t = this.treeMap.getBoundingBox(id);
    this.zoomToBox(t.x1,t.y1,t.x2,t.y2, 0.5);
};


NYTG.ZoomWindow.prototype.showInfoPane = function(id) {
    var d,p, html;
    
    d = this.treeMap.findFromId(id);
    // p = this.treeMap.findFromId(d.pid);
    html = ""
    html += "<p class='nytg-infoPane-parent'>"+d.pname+"</p>";
    html += "<p class='nytg-infoPane-label'>"+d.label+" ("+d.discretion+")</p>";
    html += "<table>"
    html += "<tr><td class='nytg-infoPane-header'>2012 Amount:</td>"
    html += "<td class='nytg-infoPane-amount'>$"+this.formatNumber(d.size*1000, 0)+"</td></tr>";
    html += "<tr><td class='nytg-infoPane-header'>Per Household:</td>"
    html += "<td class='nytg-infoPane-amount'>$"+this.formatNumber(d.size*1000 / this.HOUSEHOLDS, 2)+"</td></tr>";
    html += "<tr><td class='nytg-infoPane-header'>Change from 2010:</td>"
    html += "<td class='nytg-infoPane-amount'>"+this.formatPctChange(d.change)+"</td></tr>";
    html += "</table>"
    this.infoPane.html(html)
    
};


//----------------------------------------------
// ZOOMING AND PANNING
//----------------------------------------------

// Convenience function. Initiates an animated zoom into the center of the container
NYTG.ZoomWindow.prototype.zoomIn = function () {
    this.zoom(2, true);
};

// Convenience function. Initiates an animated zoom out from the center of the container
NYTG.ZoomWindow.prototype.zoomOut = function () {
    this.zoom(0.5, true);
};

//Given a bounding box, zooms and pans to fit in view.
NYTG.ZoomWindow.prototype.zoomToBox = function(x1,y1,x2,y2,buffer) {
    var cx, cy,
        w, h;
    
    w = x2 - x1;
    h = y2 - y1;
    cx = x1 + w / 2;
    cy = y1 + h / 2;
    
    if ( !buffer ) { buffer = 0.8 };
    
    // this.zoomContainer.addClass("nytg-zoomAnimate");
    
    
    // console.log(1 / ( Math.max(w, h) ));
    this.zoomLevel = buffer / ( Math.max(w, h) );
    this.updateZoom();
    this.updateCenter(cx,cy);
    this.renderCycle(true);
    
};

//Robust zooming interface.
NYTG.ZoomWindow.prototype.zoom = function( zoomFactor) {
    
    // if (animate) {
    //     this.zoomContainer.addClass("nytg-zoomAnimate");
    // } else {
    //     this.zoomContainer.removeClass("nytg-zoomAnimate");
    // }
    
    this.zoomLevel = this.zoomLevel * zoomFactor;
    
    
    this.updateZoom();
    this.updateCenter(this.center.x, this.center.y);
    // this.renderCycle(animate);
    
};


NYTG.ZoomWindow.prototype.updateZoom = function( ) {
    var newZoom;
    
    //test bounds
    if ( this.zoomLevel < this.minZoomLevel ) {
        this.zoomLevel = this.minZoomLevel;
    } else if (this.zoomLevel > this.maxZoomLevel) {
        this.zoomLevel = this.maxZoomLevel;
    }
    
    newZoom = String(this.zoomLevel * 100) + "%";
    // this.zoomContainer.css({
    //         "width":newZoom,
    //         "height":newZoom
    //     });
    
    this.cssUpdates.width = newZoom;
    this.cssUpdates.height = newZoom;
    
    this.infoPane.hide();
    this.highlightBox.hide();
};

NYTG.ZoomWindow.prototype.updateCenter = function(xrat, yrat) {
    var newPositionX, newPositionY,
        minCenter,maxCenter,
        npx, npy;
        
    // console.log(xrat);
    
    this.center.x = xrat;
    this.center.y = yrat;
    
    minCenter = 0 + 0.5 / this.zoomLevel;
    maxCenter = 1 - 0.5 / this.zoomLevel;
    
    //test bounds x
    this.center.x = Math.max(minCenter, this.center.x);
    this.center.x = Math.min(maxCenter, this.center.x);
    this.center.y = Math.max(minCenter, this.center.y);
    this.center.y = Math.min(maxCenter, this.center.y);
    
    newPositionX = -100*(this.center.x * this.zoomLevel - 0.5);
    newPositionY = -100*(this.center.y * this.zoomLevel - 0.5);
    
    // if (newPositionX > 0) {
    //     newPositionX = 0
    // }
    // 
    // if (newPositionY > 0) {
    //     newPositionY = 0
    // }
    
    npx = String(newPositionX)+"%";
    npy = String(newPositionY)+"%"
    
    this.cssUpdates.left = npx;
    this.cssUpdates.top = npy;
    
    // this.zoomContainer.css({
    //         "left":npx,
    //         "top":npy
    //     });
    
};


NYTG.ZoomWindow.prototype.renderCycle = function(animate) {
    if (animate) {
        this.zoomContainer.addClass("nytg-zoomAnimate");
    } else {
        this.zoomContainer.removeClass("nytg-zoomAnimate");
    }
    // console.log("render cycle")
    this.zoomContainer.css(this.cssUpdates);
    this.cssUpdates = {};
};



//----------------------------------------------
// UTILS
//----------------------------------------------

NYTG.ZoomWindow.prototype.projectFromFrameToContainer = function(x,y) {
    var xpos, ypos;
    
    xpos = this.center.x + ( x / this.frameSize.width - 0.5 ) / this.zoomLevel;
    ypos = this.center.y + ( y / this.frameSize.height - 0.5 ) / this.zoomLevel;
    // 
    // this.center.x 
    // 
    // newPositionX = -100*(this.center.x * this.zoomLevel - 0.5);
    
    return {x:xpos,y:ypos}
};

NYTG.ZoomWindow.prototype.projectContainerToFrame = function(x,y) {
    var xpos, ypos;
    
    
    return {x:xpos,y:ypos}
};



NYTG.ZoomWindow.prototype.resize = function() {
    var offset;
    this.pageWidth = this.j(document).width();
    this.pageHeight = this.j(document).height();
    this.frameSize.width = this.zoomFrame.width();
    this.frameSize.height = this.zoomFrame.height();
    offset = this.zoomFrame.offset();
    this.frameSize.x = offset.left;
    this.frameSize.y = offset.top;
};


NYTG.ZoomWindow.prototype.formatPctChange = function(n,decimals) {
    // console.log(n)
    if (n > 0) {
        return "+" + n.toFixed(1) + "%";
    } else if (n < 0) {
        return n.toFixed(1) + "%";
    } else if (n === 0){
        return "No change";
    } else {
        return "N.A."
    }
};


NYTG.ZoomWindow.prototype.formatNumber = function(n,decimals) {
    var s, remainder, num, prefix, suffix;
    // console.log(n);
    suffix = ""
    if (n >= 1000000000000) {
        suffix = " trillion"
        n = n / 1000000000000
        decimals = 2
    } else if (n >= 1000000000) {
        suffix = " billion"
        n = n / 1000000000
        decimals = 2
    } else if (n >= 1000000) {
        suffix = " million"
        n = n / 1000000
        decimals = 2
    } 
    
    
    prefix = ""
    if (decimals > 0) {
        if (n<1) {prefix = "0"};
        s = String(Math.round(n * (Math.pow(10,decimals))));
        if (s < 10) {
            remainder = "0" + s.substr(s.length-(decimals),decimals);
            num = "";
        } else{
            remainder = s.substr(s.length-(decimals),decimals);
            num = s.substr(0,s.length - decimals);
        }
        // console.log(s)
        
        
        // console.log(num.replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,") + "." + remainder)
        return prefix + num.replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,") + "." + remainder + suffix;
    } else {
        s = String(Math.round(n));
        s = s.replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
        return s + suffix;
    }
};

