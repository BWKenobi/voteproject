$(document).ready(function() {
    $('.togle').click(function(){
        parent = $(this).parent().parent();
        child = parent.children('ul');
        child.toggleClass('d-none');

        p=0;

        return false;
    });
});

$(document).ready(function() {
    $('.show-loader').click(function(){
        var invalidFields = $('form').find(":invalid");
        if (invalidFields.length==0)
            $('.content-blocker').show();

    });
});
