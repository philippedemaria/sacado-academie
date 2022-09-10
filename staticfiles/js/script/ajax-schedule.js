define(['jquery', 'bootstrap','moment', 'fullcalendar'], function ($) {
    $(document).ready(function () {
        console.log("chargement JS ajax-schedule.js OK");


		$('.update_event_modal').on('click', function () { 
		$('#show_event').modal('hide');
		});

 
 
        $('#choose_data').change(function () {
                        if ($('#choose_data').is(":checked")) {
                            $('#lesson').show(500);
                            $('#slot').hide(500);
                        } else {
                            $('#lesson').hide(500);
                            $('#slot').show(500);
                        }
                    });
  


		$('.selector_color').on('click', function () {
		    let color = $(this).attr("data-color");
		    let code = $(this).attr("data-code");
		$('#selected_color').html("<i class='fa fa-square text-"+color+"'></i>");
		$('#id_color').val("#"+code);
		});


		$(".calendar").fullCalendar({
			defaultView: 'agendaWeek',
			aspectRatio: 1.5,
	        header: {
	                  left: 'prev,next today',
	                  center: 'title',
	                  right: 'month,agendaWeek,agendaDay'
	          		},

			editable: true,
	     	selectable: true,
	     	selectHelper: true,
			eventLimit : true,
			eventStartEditable : true, 
			monthNames: ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet',
	                  'Août','Septembre','Octobre','Novembre','Décembre'],
	        monthNamesShort: ['Janv.','Févr.','Mars','Avr.','Mai','Juin','Juil.','Août','Sept.','Oct.','Nov.','Déc.'],
	        dayNames: ['Dimanche','Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi'],
	        dayNamesShort: ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'],
	        firstDay:1, // Lundi premier jour de la semaine
	        buttonText: {
	              today:    'Aujourd\'hui',
	              month:    'Mois',
	              week:     'Semaine',
	              day:      'Jour'
	          },
				events: '../events_json',	                  
			select: function(startDate) {
						$("#new_event").modal('show');  
						$(".start_hour").val(startDate.format("HH:mm")); 
						$("#id_date").val(startDate.format("YYYY-MM-DD")); 
						$("#id_date").val(startDate.format("YYYY-MM-DD"));
						$("#id_datetime").val(startDate.format("YYYY-MM-DD"));
			    },
	        eventDrop: function(event, delta, revertFunc) {

				if (!confirm(event.title + " est déplacé au " + event.date.format()+". Etes-vous sûr de ce changement ?")) {
				      revertFunc();
				    }
				else
				    {
					let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
					$.ajax(
			                {
			                    type: "POST",
			                    dataType: "json",
			                    data: {
			                       'event_id': event.id,
			                       'start_event': event.date.format(),
			                        csrfmiddlewaretoken: csrf_token
			                    },
			                    url: "shift_event" ,
			                    success: function (data) {
										console.log("OK");
			                    }
			                }
			            )
				    }

				  },
			eventClick: function(event, element) {


				let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

					$.ajax(
			                {
			                    type: "POST",
			                    dataType: "json",
			                    data: {
			                       'event_id': event.id,
			                        csrfmiddlewaretoken: csrf_token
			                    },
			                    url: "../show_event" ,
			                    success: function (data) {
			                    $("#formulaire").html("").append(data.html); 
			                    }
			                }
			            )

			    $("#show_event").modal('show');

			  }
		}) ;




        $('.display_calendar').on('click', function (event) {
            
            let teacher_id = $(this).data("teacher_id");
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
 
            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'teacher_id': teacher_id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "../ajax_display_calendar",
                    success: function (data) {

                        $('#show_teacher_name').html("").html(data.name);
                        // $('#show_teacher_calendar').html("").html(data.html);
                    }
                }
            )
        }); 















				
	}); 

})

			
           