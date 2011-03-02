/*
 * visualizer unit tests
 */
module("visualizer");

test("isContained: is a point contained in a rectangle", function() {
	ok(isContained([1,2], [1,1,3,3]), "Point at the boder is contained");
	ok(isContained([1,1], [1,1,3,3]), "Point at the edge is contained");
	ok(isContained([3,3], [1,1,3,3]), "Point at the oposite edge is contained");
	ok(isContained([2,2], [1,1,3,3]), "Point in the middle is contained");
	ok(!isContained([4,4], [1,1,3,3]), "Point outside is not contained");
});


test("formatTooltip: takes a JSON datastructure and formats it as tooltip", function() {
    data = {"name": "test1", "data": {"key1": "value1"}};
    result = "<b>test1</b><br/>key1: value1"    
	equals(formatTooltip(data), result);
});

/*
test("keydown END on handle sets value to max", function() {
	el = $('<div></div>');
	options = {
		max: 5,
		min: -5,
		orientation: 'horizontal',
		step: 1
	};
	el.slider(options);

	el.slider("value", 0);

	handle().simulate("keydown", { keyCode: $.ui.keyCode.END });
	equals(el.slider("value"), options.max);

	el.slider('destroy');	

	el = $('<div></div>');
	options = {
		max: 5,
		min: -5,
		orientation: 'vertical',
		step: 1
	};
	el.slider(options);

	el.slider("value", 0);

	handle().simulate("keydown", { keyCode: $.ui.keyCode.END });
	equals(el.slider("value"), options.max);

	el.slider('destroy');
});
*/


