define(['jquery','bootstrap_popover', 'bootstrap' ], function ($) {
    $(document).ready(function () {
        console.log("chargement JS inside_data_tab.js OK");

        $('.dataTables_filter').append(" <a  href='#' title='Version √©tablissement requise'   style='float:left' class='btn btn-success btn-xs'> Aide </a>  ");
        $('.dataTables_length').append("  <a href='#' title='Version √©tablissement requise'   class='btn btn-default pull-right'>Exporter les comp√©tences</a>  ") ;

    });
});