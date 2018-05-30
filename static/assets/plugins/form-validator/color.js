/** File generated by Grunt -- do not modify
 *  JQUERY-FORM-VALIDATOR
 *
 *  @version 2.3.77
 *  @website http://formvalidator.net/
 *  @author Victor Jonsson, http://victorjonsson.se
 *  @license MIT
 */
!function(a,b){"function"==typeof define&&define.amd?define(["jquery"],function(a){return b(a)}):"object"==typeof module&&module.exports?module.exports=b(require("jquery")):b(a.jQuery)}(this,function(a){!function(a){a.formUtils.registerLoadedModule("color");var b=function(a){return/^(\-|\+)?([0-9]+(\.[0-9]+)?|Infinity)$/.test(a)?Number(a):NaN},c=function(a){return a>0&&a<1},d=function(b){return Math.floor(b)===b&&a.isNumeric(b)};a.formUtils.addValidator({name:"hex",validatorFunction:function(a,b){if("true"===b.valAttr("allow-transparent")&&"transparent"===a)return!0;var c="#"===a[0];if(!c)return!1;var d=4===a.length||7===a.length;if(d){var e=/[0-9a-f]/i,f=a.slice(1).split(""),g=!0;return f.forEach(function(a){null===a.match(e)&&(g=!1)}),g}return!1},errorMessage:"",errorMessageKey:"badHex"}),a.formUtils.addValidator({name:"rgb",validatorFunction:function(a,b){if("true"===b.valAttr("allow-transparent")&&"transparent"===a)return!0;var c=a.replace(/ /g,""),e=/rgb\([0-9]{1,3},[0-9]{1,3},[0-9]{1,3}\)/i;if(c.match(e)){var f=c.replace(/rgb/g,""),g=f.replace(/\(/g,"").replace(/\)/g,""),h=g.split(","),i=!0;return h.forEach(function(a){var b=parseInt(a,10);(d(b)&&0<=b&&b<=255)===!1&&(i=!1)}),i}return!1},errorMessage:"",errorMessageKey:"badRgb"}),a.formUtils.addValidator({name:"rgba",validatorFunction:function(a,e){if("true"===e.valAttr("allow-transparent")&&"transparent"===a)return!0;var f=a.replace(/ /g,""),g=/rgba\([0-9]{1,3},[0-9]{1,3},[0-9]{1,3},[0,1]?.?[0-9]*\)/i;if(f.match(g)){var h=f.replace(/rgba/g,""),i=h.replace(/\(/g,"").replace(/\)/g,""),j=i.split(","),k=!0;return j.forEach(function(a,e){var f=b(a);if(d(f)){var g=f>=0&&f<=255;g||(k=!1),k&&3===e&&(k=f>=0&&f<2)}else c(a)||(k=!1)}),k}return!1},errorMessage:"",errorMessageKey:"badRgba"}),a.formUtils.addValidator({name:"hsl",validatorFunction:function(a,b){if("true"===b.valAttr("allow-transparent")&&"transparent"===a)return!0;var c=a.replace(/ /g,""),e=/hsl\(-?[0-9]{1,3},[0-9]{1,3}%,[0-9]{1,3}%\)/i;if(c.match(e)){var f=c.replace(/hsl/g,""),g=f.replace(/\(/g,"").replace(/\)/g,""),h=g.split(","),i=!0;return h.forEach(function(a,b){var c=parseInt(a,10);if(d(c)){if(0!==b){var e=c>=0&&c<=100;e||(i=!1)}}else i=!1}),i}return!1},errorMessage:"",errorMessageKey:"badHsl"}),a.formUtils.addValidator({name:"hsla",validatorFunction:function(a,c){if("true"===c.valAttr("allow-transparent")&&"transparent"===a)return!0;var e,f=a.replace(/ /g,""),g=/hsla\(-?[0-9]{1,3},[0-9]{1,3}%,[0-9]{1,3}%,[0,1]?.?[0-9]*\)/i;if(f.match(g)){var h=f.replace(/hsla/g,""),i=h.replace(/\(/g,"").replace(/\)/g,""),j=i.split(","),k=!0;return j.forEach(function(a,c){var f=b(a),g=parseInt(a,10);d(f)?(0!==c&&3!==c&&(e=f>=0&&f<=100,e||(k=!1)),k&&3===c&&(k=f>=0&&f<2)):isNaN(f)&&d(g)?(e=g>=0&&g<=100,e||(k=!1)):(f=b(Number(a).toFixed(20)),e=f>=0&&f<=1,e||(k=!1))}),k}return!1},errorMessage:"",errorMessageKey:"badHsla"})}(a)});