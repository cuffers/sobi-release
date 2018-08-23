var pos_tags = {"CC":"Coordinating conjunction","CD":"Cardinal number","DT":"Determiner","EX":"Existential there","FW":"Foreign word","IN":"Preposition or subordinating conjunction","JJ":"Adjective","JJR":"Adjective, comparative","JJS":"Adjective, superlative","LS":"List item marker","MD":"Modal","NN":"Noun, singular or mass","NNS":"Noun, plural","NNP":"Proper noun, singular","NNPS":"Proper noun, plural","PDT":"Predeterminer","POS":"Possessive ending","PRP":"Personal pronoun","PRP$":"Possessive pronoun","RB":"Adverb","RBR":"Adverb, comparative","RBS":"Adverb, superlative","RP":"Particle","SYM":"Symbol","TO":"to","UH":"Interjection","VB":"Verb, base form","VBD":"Verb, past tense","VBG":"Verb, gerund or present participle","VBN":"Verb, past participle","VBP":"Verb, non-3rd person singular present","VBZ":"Verb, 3rd person singular present","WDT":"Wh-determiner","WP":"Wh-pronoun","WP$":"Possessive wh-pronoun","WRB":"Wh-adverb"}

function generateReport() {
  var xhr = new XMLHttpRequest()
  xhr.open("POST", "/api/report");
  xhr.onload = function (event) {
      results = JSON.parse(event.target.response)[0]
      $('#results').empty()
      for(var i in results['significant_features']){
        $('#results').append('<tr>')
        var featureSplit = results['significant_features'][i][0].split('_')
        
        if(results['significant_features'][i][2]<results['significant_features'][i][3]){
          $('#results').append('<td> use more of </td>')          
        } else {
          $('#results').append('<td> use less of </td>')
        }
        
        if(featureSplit[0]==='count'||featureSplit[0]==='emoji'){
          $('#results').append('<td>"'+featureSplit[1]+'"</td>')
        }
        else if(featureSplit[0]==='pos'){
          $('#results').append('<td>'+pos_tags[featureSplit[1]]+' tagged words </td>')
        }
        else {
          $('#results').append('<td>'+results['significant_features'][i][0]+'</td>')
        }
        $('#results').append("</tr>")
      }

      document.getElementById('d-score').innerHTML = 'Distinctiveness Score: '+results['dist'].toFixed(2)
      
      var regex = buildMatchString(results['significant_features'])
      if(regex.length>0){
        $('textarea').highlightWithinTextarea({
          highlight: new RegExp(regex, "gi")
        })
      }
  };
  var formData = new FormData(document.getElementById("text-to-analyse"));
  xhr.send(formData)
}

function buildMatchString(significant_features) {
  var matchString = ''
  for(var i in significant_features){
    var featureSplit = significant_features[i][0].split('_')
    if(featureSplit[0]==='count'){
      if(parseInt(i)>0){
        matchString += '|'
      } else {
        matchString = '\\b('
      }
      matchString += featureSplit[1]
    }
  }
  if(matchString.length > 0){
    matchString += ')\\b'
  }
  console.log(matchString)
  return matchString
}