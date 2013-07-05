populateHostsGroups = function(hostSelector, groupSelector){
	hostUl = $(hostSelector);
	groupUl = $(groupSelector);
	$.get("/api/inventory",
		function(inventory, status){
			hostUl.empty();
			groupUl.empty();

			for (var i in inventory) {
				if (inventory[i]["type"] == "host"){
					hostUl.append("<li>" + inventory[i]["name"] + "</li>");
				} else if (inventory[i]["type"] == "group"){
					groupUl.append("<li>" + inventory[i]["name"] + "</li>");
				} else {
					console.error("Unknown inventory type for object: " + inventory[i]);
				}
			}
		}
	);
};

populateModules = function(selector){
	target = $(selector);
	$.get("/api/modules",
		function(modules, status){
			for (var i in modules) {
				target.append("<li>" + modules[i]["name"] + "</li>");
			}
		}
	);
};

runCommand = function(hosts, module, attr, callback){
	$.get("/api/runcommand?host=" + hosts + "&module=" + module + "&attr=" + attr,
		callback
	);
};

listenFormSubmit = function(selector){
	$(selector).submit(function() {
		formEl = $(selector);
		hosts = $("#hostsInput").val();
		module = $("#moduleInput").val();
		attr = $("#attrInput").val();
		$("#resultsBox").html("<p>Loading...</p>");
		$("#resultsBox").show();
		runCommand(hosts, module, attr, function(data){
			res = JSON.stringify(data.runresult)
			res = res.replace(/\\n/g, "<br>");
			res = res.replace(/\\t/g, "&nbsp;&nbsp;&nbsp;&nbsp;");
			$("#resultsBox").html("<h4>Results</h4><p>"+ res + "</p>");
			$("#resultsBox").show();
		});
		return false;
	});
}

$(document).ready(function(){
    // JQuery loaded
    populateHostsGroups("#hostlist", "#grouplist");
    populateModules("#modulelist");

    listenFormSubmit("#runCommandForm");
});