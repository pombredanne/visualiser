/* AG-master 13.06.25-24 (2013-06-25 11:42:54 CEST) */
rsinetsegs=['H07707_10044','H07707_10638','H07707_0'];
                var rsiExp=new Date((new Date()).getTime()+2419200000);
                var rsiDom='';
                var rsiSegs="";
                var rsiPat=/.*_5.*/;
		var i=0;
                for(x=0;x<rsinetsegs.length&&i<35;++x){if(!rsiPat.test(rsinetsegs[x])){rsiSegs+='|'+rsinetsegs[x];++i;}}
                document.cookie="rsi_segs="+(rsiSegs.length>0?rsiSegs.substr(1):"")+";expires="+rsiExp.toGMTString()+";path=/;domain="+rsiDom;
                if(typeof(DM_onSegsAvailable)=="function"){DM_onSegsAvailable(['H07707_10044','H07707_10638','H07707_0'],'h07707');}