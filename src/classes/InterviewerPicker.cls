public class InterviewerPicker{

		private Boolean firstTime {
			get{
				if (firstTime == null) firstTime = true;
				return firstTime;
			}
			set;
		}
		public String searchText { get; set; }
		public Position__c position {
			get{
				if (position == null) {
					position = [select id,name,department__c from position__c where id=:ApexPages.currentPage().getParameters().get('id')];
				}
				return position;
			}
			set;
		}
		public List<User> results {
			get{
				if (firstTime) {
				  firstTime = false;
					results = [select id, name, title, interview_dept__c from User where interview_dept__c = :position.department__c order by name];
					if (results.size() > 0){
							selected = new Interviewer__c();
							selected.Employee__c = results[0].Id;
					}
				}
				return results;
			}
			set;
		}
		public String applyInterviewerId {
			get;
			set{
				applyInterviewerId = value;
			}
		}

		private Map<String,Interviewer__c> interviewerMap {
			get{
				// build the map of the 4 interviewers (General, Technical, Managerial, Functional)
				if (interviewerMap == null){
					Map<String,Interviewer__c> tmpMap = new Map<String,Interviewer__c>();
					for(Interviewer__c interviewer:[Select i.Id,i.Name, i.Position__c,i.Employee__c,i.Employee__r.Name,i.Role__c From
							Interviewer__c i where i.Position__c=:ApexPages.currentPage().getParameters().get('id')
							order by i.Employee__r.Name]){
						if (interviewer.Role__c != null){
							if (interviewer.Role__c.toLowerCase() == 'functional'){
								if (!tmpMap.containsKey('functional')){
									tmpMap.put('functional',interviewer);
								} else {
									Interviewer__c i = new Interviewer__c();
									tmpMap.put('functional',i);
								}
							} else if(interviewer.Role__c.toLowerCase() == 'technical'){
								if (!tmpMap.containsKey('technical')){
									tmpMap.put('technical',interviewer);
								} else {
									Interviewer__c i = new Interviewer__c();
									tmpMap.put('technical',i);
								}
							} else if(interviewer.Role__c.toLowerCase() == 'managerial'){
								if (!tmpMap.containsKey('managerial')){
									tmpMap.put('managerial',interviewer);
								} else {
									Interviewer__c i = new Interviewer__c();
									tmpMap.put('managerial',i);
								}
							} else if(interviewer.Role__c.toLowerCase() == 'general'){
								if (!tmpMap.containsKey('general')){
									tmpMap.put('general',interviewer);
								} else {
									Interviewer__c i = new Interviewer__c();
									tmpMap.put('general',i);
								}
							}
						}
					}
					interviewerMap = tmpMap;
				}
				return interviewerMap;
			}
			set;
		}

		public Interviewer__c functional {
			get{
				if (interviewerMap.containsKey('functional')){
					functional = interviewerMap.get('functional');
				} else {
					Interviewer__c i = new Interviewer__c();
					interviewerMap.put('functional',i);
					functional = i;
				}
				return functional;
			}
			set;
		}

		public Interviewer__c technical {
			get{
				if (interviewerMap.containsKey('technical')){
					technical = interviewerMap.get('technical');
				} else {
					Interviewer__c i = new Interviewer__c();
					interviewerMap.put('technical',i);
					technical = i;
				}
				return technical;
			}
			set;
		}

		public Interviewer__c general {
			get{
				if (interviewerMap.containsKey('general')){
					general = interviewerMap.get('general');
				} else {
					Interviewer__c i = new Interviewer__c();
					interviewerMap.put('general',i);
					general = i;
				}
				return general;
			}
			set;
		}

		public Interviewer__c managerial {
			get{
				if (interviewerMap.containsKey('managerial')){
					managerial = interviewerMap.get('managerial');
				} else {
					Interviewer__c i = new Interviewer__c();
					interviewerMap.put('managerial',i);
					managerial = i;
				}
				return managerial;
			}
			set;
		}

		public Interviewer__c selected {
			get{
				if (firstTime) {
					// String d = [select id, Department__c from Position__c where id =:ApexPages.currentPage().getParameters().get('id')].Department__c;
					results = [select id, title, name, interview_dept__c from User where interview_dept__c = :position.department__c order by name];
					if (results.size() > 0){
							selected = new Interviewer__c();
							selected.Employee__c = results[0].Id;
							selected.Role__c = '';
							selected.employee__r = results[0];
							applyInterviewerId = results[0].Id;
					}
				} else {
					if (selected == null) {
						selected = new Interviewer__c(Role__c = role, Position__c = position.Id);
						if (applyInterviewerId != null){
							selected.Employee__c = applyInterviewerId;
							selected.Employee__r = new Map<ID,User>(results).get(applyInterviewerId);
						}
					}
				}
				return selected;
			}
			set;
		}

		public String role{
			get{
				if (role == null) {role = 'General';}
				return role;
			}
			set;
		}

		public PageReference changeRole(){
			// If the role changes we want to clone the currently selected interviewer record
			//  and make a new copy so we can insert it if necessary.  if we don't clone it
			//	then the selected interviewer may already have an id value which would
			//	prevent it from being inserted
			selected = selected.clone(false,true);
			return null;
		}

		public PageReference doSearch() {
				results = (List<User>)[FIND :searchText IN ALL FIELDS RETURNING User(Id, Name, title, Interview_Dept__c)] [0];
				return null;
		}

		public PageReference changeSelected() {
			// Create a new selected interviewer object
			selected = new Interviewer__c(Role__c = role, Position__c = position.Id);
			if (applyInterviewerId != null){
				// Set the employee id, then get the user record from the list of results
				selected.Employee__c = applyInterviewerId;
				selected.Employee__r = new Map<ID,User>(results).get(applyInterviewerId);
			}
			return null;
		}

		public PageReference doUpdateInterviewers() {
				Boolean roleMatchFound = true;
				Boolean roleSelected = true;
				// Change this to be a single, array unnecessary
				Interviewer__c deleteMe;

				if (selected.Role__c == 'Functional') {
						if (functional.id != null) {
							deleteMe = functional;
						} else { roleMatchFound = false; }
				} else if (selected.Role__c == 'Technical') {
						if (technical.id != null) {
							deleteMe = technical;
						} else { roleMatchFound = false; }
				} else if (selected.Role__c == 'General') {
						if (general.id != null) {
							deleteMe = general;
						} else { roleMatchFound = false; }
				} else if (selected.Role__c == 'Managerial') {
						if (managerial.id != null) {
							deleteMe = managerial;
						} else { roleMatchFound = false; }
				} else {
					roleSelected = false;
				}

				if (roleSelected) {
						if (roleMatchFound) {
								System.debug(deleteMe);
								delete deleteMe;
						}

						if (selected.Position__c == null) {
								selected.Position__c = position.Id;
						}
						// Make sure the record doesn't already have an id, if it does
						// then clone it and insert the clone.
						//	-- this can happen when adding the same person to be the interviewer
						//		for multiple roles
						if (selected.id != null) selected = selected.clone(false,true);
						insert selected;
						interviewerMap.put(selected.Role__c.toLowerCase(),selected);
				}
			return null;
		}

		public PageReference cancel() {
			// Declare standard controller to navigate
			ApexPages.standardController controller = new ApexPages.standardController(position);

			return controller.view();
		}
}