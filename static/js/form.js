$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				playnum : $('#usernameInput').val(),
			},
			type : 'POST',
			url : '/processuser'
		})
		.done(function(data) {

			if (data.error) {
				$('#errorAlert').text(data.error).show();
				$('#successAlert').hide();
				$('#nextButton').hide();
			}
			else {
				$('#successAlert').html((function() {
					return 'Hello ' + (data.username) + '! You have ' +
					(data.numgames) + ' games in your collection. ';
				  })).show();
				$('#errorAlert').hide();
				$('#nextButton').show();
			}

		});

		event.preventDefault();

	});

});