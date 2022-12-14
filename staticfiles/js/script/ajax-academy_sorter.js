define(['jquery', 'bootstrap', 'ui', 'ui_sortable'], function ($) {
    $(document).ready(function () {
        console.log("chargement JS ajax-academy_sorter.js OK");
 

        function sorter_sequence_academy($div_class) {

                $($div_class).sortable({
                    cursor: "move",
                    swap: true,    
                    animation: 100,
                    distance: 5,
                    revert: true,
                    tolerance: "pointer" , 
                    start: function( event, ui ) { 
                           $(ui.item).css("box-shadow", "10px 5px 10px gray"); 
                       },
                    stop: function (event, ui) {

                        var valeurs = "";
                        let parcours_id = $(this).attr("data-parcours_id");   

    

 
                        $("#sequence_sorter_academy"+parcours_id+" .relationship_id_sequence").each(function() {
                            let div_exercise_id = $(this).val();
                            valeurs = valeurs + div_exercise_id +"-";
                        });
   


                        $(ui.item).css("box-shadow", "0px 0px 0px transparent");  

                        $.ajax({
                                data:   { 'valeurs': valeurs ,} ,    
                                type: "POST",
                                dataType: "json",
                                url: "../../../qcm/ajax/sort_sequence" 
                            }); 
                        }
                    });
                }    

        sorter_sequence_academy('.sequence_sorter_academy');
        
        

    });        
});