define(['jquery',  'bootstrap', 'ui' , 'ui_sortable' , 'uploader','config_toggle'], function ($) {
    $(document).ready(function () {


    console.log(" ajax-quizz-list chargé ");


        $('.dataTables_wrapper').last().find('.col-sm-6').first().append("<h2 class='thin sacado_color_text'><i class='bi bi-list-task'></i> hors dossier </h2> ") ;




        $(document).on('click', '.quizz_to_pdf_modal', function (event) {

        	idq = $(this).data("idq")
        	$("#index_idq").val(idq);

        	title = $(this).data("title");
        	$("#idq_title").append(title);



            });






 
    });
});