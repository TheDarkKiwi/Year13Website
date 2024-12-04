
$(document).ready(function(){



    $(".tagItem").click(function(){

        let tagField = $('#tags');
        let previousFields = tagField.val();
        let thisTag = this.id;
        // console.log(thisTag);
        let newFields = previousFields+', '+thisTag;

        if (newFields.charAt(0) == ',') {
            newFields = newFields.substring(1);
        }

        tagField.val(newFields);

        $(this).fadeOut(120);
    });



    $(".tagItem").hover(function(){
        document.body.style.cursor = "pointer";
    });

 


})