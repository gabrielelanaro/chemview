// Display color scales

define(['jquery'], function($) {

    function intToRGB(i) {
        var c = (i & 0x00FFFFFF)
            .toString(16)
            .toUpperCase();

        return "#" + "00000".substring(0, 6 - c.length) + c;
    };

    var ColorScale = function($el, colors, values) {
        // Create several divs
        var width = 50,
            height = 50;
        var cell_tpl = $('<div/>');
        var list = $('<div/>');

        for (var i = 0; i < colors.length; i++) {
            var cell = cell_tpl.clone();
            cell.width(width)
                .height(height)
                .css("background-color", intToRGB(colors[i]))
                .css('display', 'inline-block')
                .css('text-align', 'center')
                .css('line-height', height + 'px')
                .text(values[i]);

            list.append(cell);
        };

        $el.append(list);
    };

    return ColorScale;

});
