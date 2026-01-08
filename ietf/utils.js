//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
//     Unless required by applicable law or agreed to in writing, software
//     distributed under the License is distributed on an "AS IS" BASIS,
//     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//     See the License for the specific language governing permissions and
//     limitations under the License.

var shortNames = new Map([['Antoni', 'Tony'], ['Anthony', 'Tony'], ['Frederick', 'Fred'], ['James', 'Jim'], ['Timothy','Tim'],
        ['Michael', 'Mike'], ['Mickael', 'Mike'], ['Michał', 'Mike'], ['Michal', 'Mike'], ['Michel', 'Mike'],
	['Stephen', 'Steve'], ['Stephan', 'Steve'], ['Steven', 'Steve'], ['Robert', 'Bob'],
        ['Nicolas', 'Nick'], ['Nicholas', 'Nick'], ['Nicklas', 'Nick'], ['Wesley', 'Wes'],
        ['Edward', 'Ted'], ['Ed', 'Ted'], ['Patrick', 'Pat'], ['Patrik', 'Pat'],['Deborah', 'Deb'], ['Benjamin', 'Ben'],
        ['Louis', 'Lou'], ['Godred', 'Gorry'], ['Russell', 'Russ'], ['Lester', 'Les'],
        ['André', 'Andre'], ['Luc André', 'Luc Andre'],['Matthew', 'Mat'],
        ['Göran', 'Goeran'], ['Hernâni', 'Hernani'], ['Frédéric', 'Frederic'],
        ['Daniel', 'Dan'], ['Jürgen', 'Jurgen'], ['Juergen', 'Jurgen'],
        ['Jörg', 'Jorg'], ['Joerg', 'Jorg'], ['Juan Carlos', 'Juan-Carlos'],
        ['Olorunlob', 'Loba'], ['Bradford', 'Brad'],['Gábor', 'Gabor'],
        ['Geoffrey', 'Geoff'], ['Balázs', 'Balazs'], ['János', 'Janos'], ['Éric', 'Eric'],
        ['Alexandre', 'Alex'], ['Alexander', 'Alex'],['Gregory', 'Greg'],['Gregory', 'Greg'],
        ['Christopher', 'Chris'], ['Christophe', 'Chris'], ['Samuel', 'Sam'], ['Richard', 'Dick'],
        ['Thomas', 'Tom'], ['Tommy', 'Tom'],
	['Jonathan', 'Jon'],
	['David', 'Dave'], ['Bernard', 'Bernie'], ['Peter', 'Pete'], ['Donald', 'Don'],
	['Shu-Fang', 'Shufang']
]) ;
//
// Find a participants based on "first last" in the participants table containing lastname firstname
function findParticipantByName(fullName, table) {
        if (! fullName) return false ;
        // Exceptions, i.e., maps some well-known names (per I-D, leadership) into registration 'official' name
        if (fullName == 'Ines Robles') fullName = 'Maria Ines Robles' ;
//        if (fullName == 'Spencer Dawkins') fullName = 'Paul Spencer Dawkins' ;
        if (fullName == 'Jose Ignacio Alvarez-Hamelin') fullName = 'J. Ignacio Alvarez-Hamelin' ;
	if (fullName == 'Juan-Carlos Zúñiga') fullName = 'Juan Carlos Zuniga' ;
	if (fullName == 'Mališa Vučinić') fullName = 'Malisa Vucinic' ;
	if (fullName == 'Carles Gomez') fullName = 'Carles Gomez Montenegro' ;
        if (fullName == 'Deb Cooley') fullName = 'Dorothy Cooley' ;
        if (fullName == 'Glenn Deen') fullName = 'Robert Glenn Deen' ;
	// Let's canonicalise the first name
        var tokens = fullName.normalize().split(' ') ;
        if (shortNames.get(tokens[0])) tokens[0] = shortNames.get(tokens[0]) ;
        // Some names out of Datatracker have a middle initial, which is not used in the registration
        var fullName2 = tokens[0] + ' ' + tokens[tokens.length-1] ;
        fullName = fullName.toUpperCase() ;
        fullName2 = fullName2.toUpperCase() ;
        for (const key in table) {
		firstName = table[key].first_name.split(' ')[0].normalize() ; // Remove all middle initials
		lastName = table[key].last_name.normalize() ;
                if (shortNames.get(firstName)) firstName = shortNames.get(firstName) ;
                var participantName = firstName + ' ' + lastName ;
                participantName = participantName.toUpperCase() ;
                if (fullName == participantName) return true ;
                if (fullName2 == participantName) return true ;
        }
        return false ;
}

function fuzzyMatch(fullName) {
	var nameDisplayed = false ;

        if (! fullName) return ;
      var table = participantsOnsite ;
//        var table = participantsRemote ;
        var tokens = fullName.split(' ') ;
        var lastName = tokens[tokens.length-1].toUpperCase() ;
	if (lastName.length <= 3) return ;
        for (let i = 0; i < table.length ; i++) {
                if (lastName == table[i][0].toUpperCase()) {
			if (! nameDisplayed) {
				console.log('Not found by exact match: ' + fullName) ;
				nameDisplayed = true ;
			}
                        console.log('  Fuzzy match with ' + table[i][1] + ' / ' + table[i][0]) ;
		}
        }
}
