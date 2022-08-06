requirejs.config({
    baseUrl: "../../../static/js", 
    waitSeconds: 90,
    paths: {
        jquery: [ 'lib/jquery-2.2.4.min'],
 
        select2: "lib/select2.full.min",
        ui: "lib/jquery-ui.min",
        ui_draggable: "script/ui-draggable",
        ui_sortable: "script/ui-sortable",
        datepicker: ["https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.7.0/js/bootstrap-datepicker.min", "lib/bootstrap-datepicker"],
        datepicker_fr: ["script/config-datepicker-fr"],
        bootstrap: "lib/bootstrap.min",
        bootstrap_popover: ["https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.6/umd/popper.min", 'lib/popper.min'], 
        ckeditor: "../ckeditor/ckeditor/ckeditor",
        ckeditor_init: "../ckeditor/ckeditor-init",
        ckeditor_jquery: "../ckeditor/ckeditor/adapters/jquery",
        toggle: ["lib/bootstrap-toggle.min"],

        colorpicker: "lib/bootstrap-colorpicker.min",
        bcPicker: "lib/bcPicker", 

        multiselect: "lib/multiselect.min",
        fastclick: "lib/fastclick.min",
        slimscroll: "lib/jquery.slimscroll.min",
        datatables: "lib/jquery.dataTables.min",
        datatables_bootstrap: "lib/dataTables.bootstrap.min",
        config_select2: "script/config-select2",
        config_datepicker: "script/config-datepicker",
        config_toggle: "script/config-toggle",
        config_datatable: "script/config-datatable", 
        config_colorpicker: "script/config-colorpicker",       
        chart:["https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.6.0/Chart.min","lib/chart.min"],   
        popper: 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min',
        fonctions_jquery: "script/fonctions-jquery",
        fonctions: "script/fonctions",
        uploader: "lib/jquery.smartuploader",
 


    },
    shim: {
        "bootstrap": {
            deps: ['jquery']
        },
        "bootstrap_popover": {
            deps: ['jquery']
        },
        "toggle": {
            deps: ['jquery',   'bootstrap']
        },
        "datepicker": {
            deps: [ 'jquery', 'bootstrap']
        },
        "multiselect": {
            deps: ['jquery', 'ui']
        },
        "slimscroll": {
            deps: ['jquery']
        },
        "ckeditor_jquery": {
            deps: ['jquery', 'ckeditor']
        },
        "ckeditor_init": {
            deps: ['jquery', 'ckeditor']
        },
        "config_toggle": {
            deps: ['jquery','toggle']
        },
        "bcPicker": {
            deps: ['jquery',]
        },
        "uploader": {
            deps: ['jquery',]
        },

    }
});

require(['jquery', 'bootstrap', 'uploader', 'bootstrap_popover', 'bcPicker', 'datatables', 'datatables_bootstrap',  'uploader', 'ckeditor_jquery',
    'ckeditor', 'ckeditor_init', 'config_select2', 'config_datepicker', 'config_toggle',  'config_colorpicker', 'fonctions_jquery',  
    'fonctions',   'config_datatable', 'multiselect', 'ui',]);
