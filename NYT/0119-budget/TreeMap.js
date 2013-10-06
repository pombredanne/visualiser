var NYTG = NYTG || {};

NYTG.TreeMap = function (data) {
    
    this.j = jQuery;
    
    this.d = data;
    this.idProp = "id";
    this.xProp = "left";
    this.yProp = "top";
    this.wProp = "width";
    this.hProp = "height";
    
    this.pxProp = "px";
    this.pyProp = "py";
    this.pwProp = "pw";
    this.phProp = "ph";
    
    this.zoomLevel = 1;
    
    this.init();
    
};

//----------------------------------------------
// CONSTRUCTOR
//----------------------------------------------

NYTG.TreeMap.prototype.init = function() {
  return this.foo + this.bar;
};


//----------------------------------------------
// PUBLIC FUNCTIONS
//----------------------------------------------

NYTG.TreeMap.prototype.getBoundingBox = function(id) {
    var obj,
        x,y,w,h;
        
    obj = this.findFromId(id);
        
    
    x = obj[this.xProp]
        
    
    // console.log(obj);
    return {x1:obj[this.xProp], y1:obj[this.yProp], x2:(obj[this.xProp] + obj[this.wProp]), y2:(obj[this.yProp] + obj[this.hProp])};
    
};



NYTG.TreeMap.prototype.findFromCoordinates = function(px,py) {
    var tx,ty,
        tw,th,
        i;
    
    for (i = this.d.length - 1; i >= 0; i--){
        tx = this.d[i][this.xProp];
        ty = this.d[i][this.yProp];
        tw = this.d[i][this.wProp];
        th = this.d[i][this.hProp];
        if ((px > tx)&&(py > ty)&&(px < tx + tw)&&(py < py + th)) {
            return this.d[i];
        }
    }
};

NYTG.TreeMap.prototype.findFromId = function(id) {
    var i;
    for (i = this.d.length - 1; i >= 0; i--){
        // console.log(this.d[i][this.idProp]);
        if (this.d[i][this.idProp] === id) {
            
            return this.d[i];
        }
    }
    throw "couldn't find: "+id
};


