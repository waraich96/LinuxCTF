$(document).ready(function(){

	$('input').first().focus();

	show_messages('.error');
	show_messages('.message');
	show_messages('.success');

	$('.taskTitle').click(function(){
		
		$(this).next().slideToggle();

	});

});

function checkAnswer( taskID ){

	var given_answer = $('#'+taskID+' input[name="answer"]').val();

	$.ajax(
		{ 	url:"/checkAnswer",
			method: "POST",
			data: { 
					"taskID": taskID,
					"answer": given_answer
				  },
			dataType: "json",

			success:(function(response){

				if ( response['correct'] == 1){
					var newTotalPoints = response['newTotalPoints'];

					say_correct( newTotalPoints );
					correctTask( taskID );
					$('#'+ taskID + ' #taskBody').slideUp();


				}
				if ( response['correct'] == 0){
					$.notify('Incorrect!', 'error');
					// say_wrong();
				}
				if ( response['correct'] == -1){
				$.notify('You have already solved this task!', 'warn');
					//say_already();
				}
	})});
	
	return false;
};

function say_correct( newTotalPoints ){

	// $('.success').text("You are correct! Nice work!");
	// show_message('success');
	
	$.notify('You are correct! Nice work!', 'success');

	$('#totalPoints').text( String(newTotalPoints) );

}

function correctTask(taskID){

	$("#" + taskID + " h3").css({
		'background-color': '#eeFFee',
		'color': '#348017',
		'border': '1px solid #254117;'
	});
}

function say_wrong(){

	$('.error').text("Incorrect!");
	show_message('error');
}


function say_already(){

	$('.message').text("You have already solved this task!");
	show_message('message');
}

function show_message(name){

	$('.' + name).slideDown();

	window.setTimeout( hide_messages, 2000 );
}

function show_messages(name){

	if ( $(name).text() != '' ){
		show_message(name.slice(1));
	}
	
}

function hide_messages( ){

	$('.message').slideUp();
	$('.error').slideUp();
	$('.success').slideUp();
}