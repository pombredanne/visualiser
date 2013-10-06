var NYTG = NYTG || {};

var console = console || {log:function(){}};


NYTG.csstransitions = Modernizr.csstransitions;

// nytg-zoomContent
// nytg-zoomFrame
// nytg-zoomIn
// nytg-zoomOut
$j = jQuery;

NYTG.zoomLevel = 1;
NYTG.zoomStep = 2;
NYTG.zoomCenter = {};
NYTG.zoomCenter.x = 0.75;
NYTG.zoomCenter.y = 0.75;

NYTG.dragStart = {};
NYTG.dragStart.x = 0;
NYTG.dragStart.y = 0;

NYTG.showingMandatory = true;
NYTG.showingDiscretionary = true;


NYTG.s = new NYTG.SearchBox("nytg-searchBox", NYTG.treeMapData, "label", "pname", "size", "id");
NYTG.tm = new NYTG.TreeMap(NYTG.treeMapData);
NYTG.z = new NYTG.ZoomWindow("nytg-treeMap", NYTG.tm);


NYTG.s.findCallback = function(obj){
    NYTG.z.annotateNode(obj["id"]);
    NYTG.z.renderCycle(true);
};

$j("#nytg-zoomIn").click(function( evt ) {
    evt.preventDefault();
    NYTG.z.zoomIn();
    NYTG.resetMandatory();
    NYTG.z.renderCycle(true);
});
$j("#nytg-zoomOut").click(function( evt ) {
    evt.preventDefault();
    NYTG.z.zoomOut();
    NYTG.resetMandatory();
    NYTG.z.renderCycle(true);
});

NYTG.resetMandatory = function() {
    NYTG.showingDiscretionary = true;
    $j("#nytg-mandatoryAnnotationLink").html("Isolate&nbsp;mandatory&nbsp;spending.");
    $j(".nytg-zoomFrame").removeClass("nytg-hideDiscretionary");
    
    NYTG.showingMandatory = true;
    $j(".nytg-zoomFrame").removeClass("nytg-hideMandatory");
    $j("#nytg-discretionaryAnnotationLink").html("Isolate&nbsp;discretionary&nbsp;spending.");
}


$j("#nytg-discretionaryAnnotationLink").click(function(evt){ 
    evt.preventDefault();
    
    if (NYTG.showingMandatory) {
        $j(".nytg-zoomFrame").addClass("nytg-hideMandatory");
        $j("#nytg-discretionaryAnnotationLink").html("Show&nbsp;all&nbsp;spending.");
    } else {
        $j(".nytg-zoomFrame").removeClass("nytg-hideMandatory");
        $j("#nytg-discretionaryAnnotationLink").html("Isolate&nbsp;discretionary&nbsp;spending.");
    }
    NYTG.showingMandatory = !NYTG.showingMandatory;
    NYTG.showingDiscretionary = true;
    $j("#nytg-mandatoryAnnotationLink").html("Isolate&nbsp;mandatory&nbsp;spending.");
    $j(".nytg-zoomFrame").removeClass("nytg-hideDiscretionary");
    
});
$j("#nytg-mandatoryAnnotationLink").click(function(evt){
    evt.preventDefault();
    
    if (NYTG.showingDiscretionary) {
        $j(".nytg-zoomFrame").addClass("nytg-hideDiscretionary");
        $j("#nytg-mandatoryAnnotationLink").html("Show&nbsp;all&nbsp;spending.");
    } else {
        $j(".nytg-zoomFrame").removeClass("nytg-hideDiscretionary");
        $j("#nytg-mandatoryAnnotationLink").html("Isolate&nbsp;mandatory&nbsp;spending.");
    }
    NYTG.showingDiscretionary = !NYTG.showingDiscretionary;
    NYTG.showingMandatory = true;
    $j(".nytg-zoomFrame").removeClass("nytg-hideMandatory");
    $j("#nytg-discretionaryAnnotationLink").html("Isolate&nbsp;discretionary&nbsp;spending.");
    

});
$j("#nytg-lowIncomeAnnotationLink").click(function(evt){ 
    evt.preventDefault();
    NYTG.z.annotateNode("leaf-118");
    NYTG.resetMandatory();
});
$j("#nytg-epaAnnotationLink").click(function(evt){ 
    evt.preventDefault();
    NYTG.z.annotateNode("leaf-424");
    NYTG.resetMandatory();
});
$j("#nytg-teachersAnnotationLink").click(function(evt){ 
    evt.preventDefault();
    NYTG.z.annotateNode("leaf-96");
    NYTG.resetMandatory();
});
$j("#nytg-energyAnnotationLink").click(function(evt){
    evt.preventDefault();
    NYTG.z.annotateNode("leaf-110");
    NYTG.resetMandatory();
});






NYTG.mapURL = "http://www.nytimes.com/packages/html/newsgraphics/2011/0119-budget/index.html"
document.getElementById('nytg-shareTwitter').href   = "http://twitter.com/share?text=Explore%20every%20nook%20and%20cranny%20of%20Obama's%202012%20Budget%20proposal&url="+NYTG.mapURL;
document.getElementById('nytg-shareFacebook').href  = "http://www.facebook.com/sharer.php?t=Explore%20every%20nook%20and%20cranny%20of%20Obama's%202012%20Budget%20Proposal&u="+NYTG.mapURL;


//fullscreen
NYTG.fullscreen = false;
$j(".nytg-fullScreenButton").click(fullScreenToggle);
function fullScreenToggle(evt) {
    NYTG.z.resize();
    evt.preventDefault();
  if (NYTG.fullscreen) {
    $j(".nytg-fullScreenButton").text("Full Screen");
    if (NYTG.csstransitions) {
        $j('#nytg-fluidHeader').css({'top':'54px'});
        $j('#nytg-fluidBody').css({'top':'118px','bottom':'46px'})
        $j('#nytg-fluidFooter').css({'bottom':'0px'});
        $j('#nytg-controlPane').css({'left':'0px'});
        $j('#nytg-mapContainer').css({'left':'280px'});
        $j('#nytg-mapHeader').css({'left':'280px'});
    }else {
        $j('#nytg-fluidHeader').animate({'top':'54px'});
        $j('#nytg-fluidBody').animate({'top':'118px','bottom':'46px'})
        $j('#nytg-fluidFooter').animate({'bottom':'0px'});
        $j('#nytg-controlPane').animate({'left':'0px'});
        $j('#nytg-mapContainer').animate({'left':'280px'});
        $j('#nytg-mapHeader').animate({'left':'280px'});
    }
    
  } else {
      $j(".nytg-fullScreenButton").text("Exit Full Screen");
      if (NYTG.csstransitions) {
          $j('#nytg-fluidHeader').css({'top':'-90px'});
          $j('#nytg-fluidBody').css({'top':'41px','bottom':'0px'})
          $j('#nytg-fluidFooter').css({'bottom':'-55px'});
          $j('#nytg-controlPane').css({'left':'-280px'});
          $j('#nytg-mapContainer').css({'left':'0px'});
          $j('#nytg-mapHeader').css({'left':'0px'});
      } else {
          $j('#nytg-fluidHeader').animate({'top':'-90px'});
          $j('#nytg-fluidBody').animate({'top':'41px','bottom':'0px'})
          $j('#nytg-fluidFooter').animate({'bottom':'-55px'});
          $j('#nytg-controlPane').animate({'left':'-280px'});
          $j('#nytg-mapContainer').animate({'left':'0px'});
          $j('#nytg-mapHeader').animate({'left':'0px'});
      }
    
  }
  NYTG.fullscreen = !NYTG.fullscreen;
}


// Analytics
var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-7885722']);
_gaq.push(['_trackPageview'])    
var ga = document.createElement('script');
ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
ga.setAttribute('async', 'true');
document.documentElement.firstChild.appendChild(ga);