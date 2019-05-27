function highlight_in(elt) {
    // apply highlight.js to everything inside ele (a jquery element).
    elt.find('pre[lang]').each(function(i, block) {
        /* adapt the github markdown output to look like creole */
        block = $(block);
        lang = block.attr('lang');
        block.addClass('highlight');
        block.addClass('lang-'+lang);
    });
    elt.find('pre.highlight').each(function(i, block) {
        hljs.highlightBlock(block);
    });
}
$(document).ready(function() {
    highlight_in($(document));
});