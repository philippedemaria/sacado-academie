requirejs.config({
    baseUrl: "../../../static/js", 
    waitSeconds: 90,
    paths: {
        jquery: ['lib/jquery-2.2.4.min'],
        select2: "lib/select2.full.min",
        ui: "lib/jquery-ui.min",
        ui_draggable: "script/ui-draggable",
        ui_sortable: "script/ui-sortable",
        datepicker: ["https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.7.0/js/bootstrap-datepicker.min", "lib/bootstrap-datepicker"],
        datepicker_fr: ["script/config-datepicker-fr"],
        bootstrap: "lib/bootstrap.min",
        popoverx: "lib/bootstrap-popover-x.min",
        ckeditor: "../ckeditor/ckeditor/ckeditor",
        ckeditor_init: "../ckeditor/ckeditor-init",
        ckeditor_jquery: "../ckeditor/ckeditor/adapters/jquery",
        toggle: ["lib/bootstrap-toggle.min"],
        colorpicker: "lib/bootstrap-colorpicker.min",
        multiselect: "lib/multiselect.min",
        mathjax: ["https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-MML-AM_CHTML&amp;delayStartupUntil=configured"],
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
        bootstrapjs: "bootstrap",
 
    },
    shim: {
        "bootstrap": {
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
        "bootstrapjs": {
            deps: ['jquery']
        },
        "config_toggle": {
            deps: ['jquery','toggle']
        },

        mathjax: {
            exports: "MathJax",
            init: function () {
                MathJax.Hub.Config({
                    extensions: ["tex2jax.js"],
                    jax: ["input/TeX", "output/HTML-CSS"],
                    tex2jax: {
                        inlineMath: [['$', '$'], ["\\(", "\\)"]],
                        displayMath: [['$$', '$$'], ["\\[", "\\]"]],
                        processEscapes: true
                    },
                    "HTML-CSS": {availableFonts: ["TeX"], scale: 90}
                });
                MathJax.Hub.Startup.onload();
                return MathJax;
            }
        }
    }
});

require(['jquery', 'bootstrap', 'mathjax', ]);

// suppression de admin dans le chargement  : 'admin', 'multiselect', 'ui',
//    'ckeditor', 'ckeditor_init', 'ckeditor_jquery', 'config_toggle', 'slimscroll', 'chart'
