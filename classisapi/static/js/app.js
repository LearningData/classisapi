$('.url').keypress(function (e) {
  if (e.which == 13) {
	var method = $('.method').find(':selected').val();
	if(method == 'post') {
	  post_query();
	} else {
	  get_query();
	}
  }
});

function change_method() {
  var method = $('.method').find(':selected').val();
  if(method == 'post') {
	$('.post-json').show();
	$('.get').hide();
	$('.post').show();
	$('#request').html('POST');
  } else {
	$('.post-json').hide();
	$('.post').hide();
	$('.get').show();
	$('#request').html('GET');
  }
}

function init_status() {
	$('.error').hide();
	$('.success').hide();
	$('.loading').toggle();
}

function change_status(status) {
	$('.loading').toggle();
	if(status == 'success') {
		$('.error').hide();
		$('.success').show();
	} else {
		$('.success').hide();
		$('.error').show();
	}
}

function display_auth() {
  $('.auth').toggle();
}

function get_auth() {
  var user = $('.user').val();
  var token = $('.token').val();
  if(user != '' && token != '') {
	return 'user=' + user + '&token=' + token
  }
  return ''
}

function display_response(jqXHR) {
  console.log(jqXHR)
  var headers = jqXHR.getAllResponseHeaders();
  $('#headers').html(headers);
  try {
	var response = JSON.parse(jqXHR.responseText);
	response = JSON.stringify(response, null, 4);
	$('#response').html(response);
  } catch(e) {
	console.log(e);
  }
}

function get_query() {
  var auth = get_auth();
  var url = $('.url').val()
  if(url != '') {
	init_status();

	$.getJSON(url + '?' + auth, function() {
	  console.log('success');
	})
	.done(function(data, status, jqXHR) {
	  $('#request').css({'color': 'green'})
	  display_response(jqXHR);
	})
	.fail(function(jqXHR, textStatus, errorThrown) {
	  $('#request').css({'color': 'red'})
	  display_response(jqXHR);
	})
	.always(function(resp, status) {
	  change_status(status);
	});
  } else {
	alert('Please enter a valid URL!');
  }
}

function post_query() {
  var auth = get_auth();
  var url = $('.url').val()
  var json = $('.json').val()

  if(url != '' && json !='') {
	init_status();

	$.ajax({
	  url: url + '?' + auth,
	  type: 'POST',
	  data: json,
	  contentType: 'application/json; charset=utf-8',
	  dataType: 'json',
	  success: function(data) {
		console.log(data);
	  }
	})
	.done(function(data, status, jqXHR) {
	  $('#request').css({'color': 'green'})
	  display_response(jqXHR);
	})
	.fail(function(jqXHR, textStatus, errorThrown) {
	  $('#request').css({'color': 'red'})
	  display_response(jqXHR);
	})
	.always(function(resp, status) {
	  change_status(status);
	});
  } else {
	alert('Please enter a valid URL and/or JSON!');
  }
}
