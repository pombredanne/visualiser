var NYTG = NYTG || {};

//requires jQuery

NYTG.SearchBox = function (nodeId, data, primaryField, alternatesField, rankingField, idField) {
    
    this.j = jQuery;
    
    this.defaultText = "Search";
    this.nodeId = nodeId;
    this.rootNode = this.j("#" + nodeId);
    this.container = this.j('<div class="nytg-search"></div>');
    this.inputNode = this.j("<input type='text' placeholder='"+this.defaultText+"' class='nytg-searchBox' spellcheck='false' autocomplete='off' title='"+this.defaultText+"'></input");
    this.resultsNode = this.j('<div class="nytg-searchResults" style="display:none;"></div>');
    this.resultsList = this.j('<ul class="nytg-resultsList"><li class="nytg-resultsSummary">Search the Federal Budget proposal.</li></ul>');
    
    this.d = data;
    this.primaryField = primaryField;
    this.alternatesField = alternatesField;
    this.rankingField = rankingField;
    this.idField = idField;
    
    this.results = [];
    this.resultsSelectIndex = 0;
    
    this.hasFakeFocus = false;
    
    this.primaryRows = [];
    this.alternatesRows = [];
    
    this.maxMatches = 10;
    this.searchTime = 0;
    
    this.findCallback = function(obj){};
    
    this.init();
    
};


//----------------------------------------------
// CONSTRUCTOR
//----------------------------------------------

NYTG.SearchBox.prototype.init = function() {
    var me = this,
        i;
    
    this.rootNode.append(this.container);
    this.container.append(this.inputNode).append(this.resultsNode.append(this.resultsList));
    this.inputNode.wrap("<div class='nytg-searchInputWrapper'></div>");
    
    
    for (i=0; i < this.d.length; i++) {
        this.primaryRows[i] = this.d[i][this.primaryField].toLowerCase() + " - "+ this.d[i][this.alternatesField].toLowerCase();
    };
    for (i=0; i < this.d.length; i++) {
        this.alternatesRows[i] = this.d[i][this.alternatesField].toLowerCase();
    };
    
    this.resultsList.bind("click", function(evt){ me.resultsClickHandler(evt) } );
    this.inputNode.bind("keyup", function(evt){me.keyUpHandler(evt)});
    this.inputNode.bind("focus", function(evt){me.focusHandler(evt)});
    this.inputNode.bind("click", function(evt){me.clickHandler(evt)});
    // this.inputNode.bind("blur", function(evt){me.blurHandler(evt)});
    // this.inputNode.bind("change", function(evt){me.changeHandler(evt)});

    this.inputNode.val(this.defaultText);

    jQuery('body').bind('click', function(e){
			if(me.container.hasClass('nytg-search-focus') && jQuery(e.target).parents('#'+me.nodeId).length == 0){
				me.blurHandler();
			}
		});
};


//----------------------------------------------
// RENDERING
//----------------------------------------------
NYTG.SearchBox.prototype.render = function(time) {
    var i, html;
    
    html = "";
    if (this.results.length === 0) {
        html += "<li class='nytg-resultsSummary'>No results.</li>";
        
    };
    for (i=0; i < this.results.length; i++) {
        if (this.d[this.results[i]]["pname"] == "all") {
            // html += "<li><a href='#'>"+"<span style='display:none;'>"+i+"</span>"+ this.d[this.results[i]][this.primaryField] + " - ($"+this.formatNumber(this.d[this.results[i]]["size"],0) +")</a></li>"
            
        } else {
            html += "<li><a href='#'><span class='nytg-searchDescription'>"+"<span class='nytg-searchIndexId' style='display:none;'>"+i+"</span>"+ this.d[this.results[i]]["pname"] + " - " + this.d[this.results[i]][this.primaryField] + " ("+this.d[this.results[i]]["discretion"] +")</span><span class='nytg-searchAmount'>$"+this.formatNumber(this.d[this.results[i]]["size"]*1000,0)+"</span></a></li>"
            
        }
    };
    this.resultsList.html(html);
    // if (this.results.length > 0) {
    //     this.resultsNode.show();
    // } else {
    //     this.resultsNode.hide();
    // }
};








//----------------------------------------------
// SEARCHING
//----------------------------------------------
NYTG.SearchBox.prototype.find = function(val){
    var matches;
    this.resultsSelectIndex = 0;
    matches = [];
    // console.log(val);
    val = val.toLowerCase();
    if (val.length === 0) {
        return matches;
    } else {
        //simple search on beginning of primary match name
        for (var i = this.primaryRows.length - 1; i >= 0; i--){
            if ( this.primaryRows[i].substr(0,val.length) === val ) {
                if (matches.indexOf(i) === -1) { matches.push(i); };
            };
            if (matches.length >= this.maxMatches) {
                // console.log(matches);
                return matches
            };
        };
        
        //search the beginning of each word
        for (var i = this.primaryRows.length - 1; i >= 0; i--){
            var words = this.primaryRows[i].split(" ")
            for (var j=0; j < words.length; j++) {
                if ( words[j].substr(0,val.length) === val ) {
                    if (matches.indexOf(i) === -1) { matches.push(i); };
                };
                if (matches.length >= this.maxMatches) {
                    // console.log(matches);
                    return matches
                };
            };
        };
        
        //least descriminating search
        for (var i = this.primaryRows.length - 1; i >= 0; i--){
            if ( this.primaryRows[i].indexOf(val) !== -1 ) {
                if (matches.indexOf(i) === -1) { matches.push(i); };
            };
            if (matches.length >= this.maxMatches) {
                // console.log(matches);
                return matches
            };
        };
        
        //search words split up
        for (var i = this.primaryRows.length - 1; i >= 0; i--){
            var searchWords = val.split(" ");
            var isMatch = true;
            for (var j=0; j < searchWords.length; j++) {
                if ( this.primaryRows[i].indexOf(searchWords[j]) === -1 ) {
                    isMatch = false;
                };
            };
            if ( isMatch ) {
                if (matches.indexOf(i) === -1) { matches.push(i); };
            };
            if (matches.length >= this.maxMatches) {
                // console.log(matches);
                return matches
            };
        };
    
    };
    
    // console.log(matches);
    return matches
};



//----------------------------------------------
// EVENTS
//----------------------------------------------

NYTG.SearchBox.prototype.clickHandler = function(evt) {
    // console.log("click");
    // evt.preventDefault();
    
    if (this.container.hasClass("nytg-search-focus")) {
        
    } else  {
        this.container.addClass("nytg-search-focus");
        this.resultsNode.show();
        if (this.inputNode.val() === this.defaultText) {
            this.inputNode.val("");
        } else {
            this.inputNode.select();
        }
    }
    
    

};

NYTG.SearchBox.prototype.focusHandler = function(evt) {
    // console.log("focus")
};

NYTG.SearchBox.prototype.blurHandler = function(evt) {
    // console.log("blur")

    this.container.removeClass("nytg-search-focus");
    this.inputNode.blur();
    this.resultsNode.hide();
    if (this.inputNode.val() === "") {
        this.inputNode.val(this.defaultText);
    };
    
};

NYTG.SearchBox.prototype.changeHandler = function(evt) {

    // console.log("change");
};

NYTG.SearchBox.prototype.keyUpHandler = function(evt) {
    var searchString,
        results,
        startTime, endTime;
    
    if (!this.container.hasClass("nytg-search-focus")) {
        this.clickHandler();
    }
    
    if (evt.keyCode === 27) { this.blurHandler(); };
    if (evt.keyCode === 13) { this.findDispatcher(); };//enter
    
    // console.log("keyPress");
    searchString = this.inputNode.val();
        
    startTime = new Date();
    this.results = this.find(searchString);
    endTime = new Date();
    this.searchTime = endTime - startTime;
    this.render(this.searchTime);
};


NYTG.SearchBox.prototype.resultsClickHandler = function(evt) {
    var resultIndex;
    evt.preventDefault();
    this.resultsSelectIndex = this.j(evt.target).find(".nytg-searchIndexId").text();
    // console.log(this.resultsSelectIndex);
    this.findDispatcher();
};

NYTG.SearchBox.prototype.findDispatcher = function() {
    var r;
    
    r = this.d[this.results[this.resultsSelectIndex]];
    
    
    // console.log(r);
    this.blurHandler();
    
    this.inputNode.val(r[this.primaryField])
    this.findCallback(r);
};



//----------------------------------------------
// UTILS
//----------------------------------------------
NYTG.SearchBox.prototype.formatNumber = function(n,decimals) {
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

if(!Array.indexOf){
	    Array.prototype.indexOf = function(obj){
	        for(var i=0; i<this.length; i++){
	            if(this[i]==obj){
	                return i;
	            }
	        }
	        return -1;
	    }
	}

