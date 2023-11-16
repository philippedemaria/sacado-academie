define(['jquery', 'bootstrap' ], function ($) {
    $(document).ready(function () {
        console.log("chargement JS ajax-invoice.js OK");


        $(document).on('change', '.this_password', function (event) {


            var value = $(this).val() ;
            if(value.length<8)
            {
                alert("Votre mot de passe doit contenir au moins 8 caractères.") ;
                return false ;
            }

                





            });




        
    });

});
 

 
 

 
 
 