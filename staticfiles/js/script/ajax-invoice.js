define(['jquery', 'bootstrap' ], function ($) {
    $(document).ready(function () {
        console.log("chargement JS ajax-invoice.js OK");


        $(".details_beneficiaire").hide();

        $("body").on('focus', '#id_beneficiaire', function (event) { 
            $(".details_beneficiaire").show();
        });      

        $("body").on('change', '#id_school', function (event) { 
            $(".details_beneficiaire").hide();
        });


        $(document).on('click', '.add_more', function (event) {


                var total_form = $('#id_subinvoices-TOTAL_FORMS') ;
                var totalForms = parseInt(total_form.val())  ;

                var thisClone = $('#rowToClone');
                rowToClone = thisClone.html() ;

                $('#formsetZone').append(rowToClone);

                $('#duplicate').attr("id","duplicate"+totalForms) 
                $('#cloningZone').attr("id","cloningZone"+totalForms) 

                $('#duplicate'+totalForms).find('.delete_button').html('<a href="javascript:void(0)" class="btn btn-danger remove_more" ><i class="fa fa-trash"></i></a>'); 
                $('#duplicate'+totalForms).find("input[type='checkbox']").bootstrapToggle();

                $("#duplicate"+totalForms+" input").each(function(){ 
                    $(this).attr('id',$(this).attr('id').replace('__prefix__',totalForms));
                    $(this).attr('name',$(this).attr('name').replace('__prefix__',totalForms));
                });

                console.log(totalForms+1);
                total_form.val(totalForms+1);
            });



        $(document).on('click', '.remove_more', function () {
            var total_form = $('#id_subinvoices-TOTAL_FORMS') ;
            var totalForms = parseInt(total_form.val())-1  ;

            $('#duplicate'+totalForms).remove();
            total_form.val(totalForms)
        });


 

 

        
    });

});
 

 
 

 
 
 