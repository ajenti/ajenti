/*
  Copyright (c) 2006-2009 Paranoid Ferret Productions.  All rights reserved.

  Developed by: Paranoid Ferret Productions
                http://www.paranoidferret.com

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to
  deal with the Software without restriction, including without limitation the
  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
  sell copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:
    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimers.
    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimers in the
       documentation and/or other materials provided with the distribution.
    3. Neither the name Paranoid Ferret Productions, nor the names of its 
       contributors may be used to endorse or promote products derived 
       from this Software without specific prior written permission.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
  CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
  WITH THE SOFTWARE.
*/

function Position(x, y)
{
  this.X = x;
  this.Y = y;
  
  this.Add = function(val)
  {
    var newPos = new Position(this.X, this.Y);
    if(val != null)
    {
      if(!isNaN(val.X))
        newPos.X += val.X;
      if(!isNaN(val.Y))
        newPos.Y += val.Y
    }
    return newPos;
  }
  
  this.Subtract = function(val)
  {
    var newPos = new Position(this.X, this.Y);
    if(val != null)
    {
      if(!isNaN(val.X))
        newPos.X -= val.X;
      if(!isNaN(val.Y))
        newPos.Y -= val.Y
    }
    return newPos;
  }
  
  this.Min = function(val)
  {
    var newPos = new Position(this.X, this.Y)
    if(val == null)
      return newPos;
    
    if(!isNaN(val.X) && this.X > val.X)
      newPos.X = val.X;
    if(!isNaN(val.Y) && this.Y > val.Y)
      newPos.Y = val.Y;
    
    return newPos;  
  }
  
  this.Max = function(val)
  {
    var newPos = new Position(this.X, this.Y)
    if(val == null)
      return newPos;
    
    if(!isNaN(val.X) && this.X < val.X)
      newPos.X = val.X;
    if(!isNaN(val.Y) && this.Y < val.Y)
      newPos.Y = val.Y;
    
    return newPos;  
  }  
  
  this.Bound = function(lower, upper)
  {
    var newPos = this.Max(lower);
    return newPos.Min(upper);
  }
  
  this.Check = function()
  {
    var newPos = new Position(this.X, this.Y);
    if(isNaN(newPos.X))
      newPos.X = 0;
    if(isNaN(newPos.Y))
      newPos.Y = 0;
    return newPos;
  }
  
  this.Apply = function(element)
  {
    if(typeof(element) == "string")
      element = document.getElementById(element);
    if(element == null)
      return;
    if(!isNaN(this.X))
      element.style.left = this.X + 'px';
    if(!isNaN(this.Y))
      element.style.top = this.Y + 'px';  
  }
}

function hookEvent(element, eventName, callback)
{
  if(typeof(element) == "string")
    element = document.getElementById(element);
  if(element == null)
    return;
  if(element.addEventListener)
  {
    element.addEventListener(eventName, callback, false);
  }
  else if(element.attachEvent)
    element.attachEvent("on" + eventName, callback);
}

function unhookEvent(element, eventName, callback)
{
  if(typeof(element) == "string")
    element = document.getElementById(element);
  if(element == null)
    return;
  if(element.removeEventListener)
    element.removeEventListener(eventName, callback, false);
  else if(element.detachEvent)
    element.detachEvent("on" + eventName, callback);
}

function cancelEvent(e)
{
  e = e ? e : window.event;
  if(e.stopPropagation)
    e.stopPropagation();
  if(e.preventDefault)
    e.preventDefault();
  e.cancelBubble = true;
  e.cancel = true;
  e.returnValue = false;
  return false;
}

function getEventTarget(e)
{
  e = e ? e : window.event;
  return e.target ? e.target : e.srcElement;
}

function absoluteCursorPostion(eventObj)
{
  eventObj = eventObj ? eventObj : window.event;
  
  if(isNaN(window.scrollX))
    return new Position(eventObj.clientX + document.documentElement.scrollLeft + document.body.scrollLeft, 
      eventObj.clientY + document.documentElement.scrollTop + document.body.scrollTop);
  else
    return new Position(eventObj.clientX + window.scrollX, eventObj.clientY + window.scrollY);
}

function dragObject(element, attachElement, lowerBound, upperBound, startCallback, moveCallback, endCallback, attachLater)
{
  if(typeof(element) == "string")
    element = document.getElementById(element);
  if(element == null)
      return;
  
  if(lowerBound != null && upperBound != null)
  {
    var temp = lowerBound.Min(upperBound);
    upperBound = lowerBound.Max(upperBound);
    lowerBound = temp;
  }

  var cursorStartPos = null;
  var elementStartPos = null;
  var dragging = false;
  var listening = false;
  var disposed = false;
  
  function dragStart(eventObj)
  { 
    if(dragging || !listening || disposed) return;
    dragging = true;
    
    if(startCallback != null)
      startCallback(eventObj, element);
    
    cursorStartPos = absoluteCursorPostion(eventObj);
    
    elementStartPos = new Position(parseInt(element.style.left), parseInt(element.style.top));
   
    elementStartPos = elementStartPos.Check();
    
    hookEvent(document, "mousemove", dragGo);
    hookEvent(document, "mouseup", dragStopHook);
    
    return cancelEvent(eventObj);
  }
  
  function dragGo(eventObj)
  {
    if(!dragging || disposed) return;
    
    var newPos = absoluteCursorPostion(eventObj);
    newPos = newPos.Add(elementStartPos).Subtract(cursorStartPos);
    newPos = newPos.Bound(lowerBound, upperBound)
    newPos.Apply(element);
    if(moveCallback != null)
      moveCallback(newPos, element, eventObj);
        
    return cancelEvent(eventObj); 
  }
  
  function dragStopHook(eventObj)
  {
    dragStop();
    return cancelEvent(eventObj);
  }
  
  function dragStop()
  {
    if(!dragging || disposed) return;
    unhookEvent(document, "mousemove", dragGo);
    unhookEvent(document, "mouseup", dragStopHook);
    cursorStartPos = null;
    elementStartPos = null;
    if(endCallback != null)
      endCallback(element);
    dragging = false;
  }
  
  this.Dispose = function()
  {
    if(disposed) return;
    this.StopListening(true);
    element = null;
    attachElement = null
    lowerBound = null;
    upperBound = null;
    startCallback = null;
    moveCallback = null
    endCallback = null;
    disposed = true;
  }
  
  this.StartListening = function()
  {
    if(listening || disposed) return;
    listening = true;
    hookEvent(attachElement, "mousedown", dragStart);
  }
  
  this.StopListening = function(stopCurrentDragging)
  {
    if(!listening || disposed) return;
    unhookEvent(attachElement, "mousedown", dragStart);
    listening = false;
    
    if(stopCurrentDragging && dragging)
      dragStop();
  }
  
  this.IsDragging = function(){ return dragging; }
  this.IsListening = function() { return listening; }
  this.IsDisposed = function() { return disposed; }
  
  if(typeof(attachElement) == "string")
    attachElement = document.getElementById(attachElement);
  if(attachElement == null)
    attachElement = element;
    
  if(!attachLater)
    this.StartListening();
}




var List;
var PlaceHolder;

function ui_initSortList(id)
{
  List = document.getElementById(id);
 
  PlaceHolder = document.createElement("DIV");
  PlaceHolder.className = "ui-el-sortlist-item";
  PlaceHolder.style.backgroundColor = "rgb(225,225,225)";
  PlaceHolder.SourceI = null;
 
  for (i=0; i<List.children.length; i++)
    if (List.children[i].className == 'ui-el-sortlist-item') 
      new dragObject(List.children[i].id, null, null, null, itemDragBegin, itemMoved,
          itemDragEnd, false);
}

function itemDragBegin(eventObj, element)
{
  element.style.top = element.offsetTop + 'px';
  element.style.left = element.offsetLeft + 'px';
  element.className = "ui-el-sortlist-drag";
  PlaceHolder.style.height = element.style.height;
  List.insertBefore(PlaceHolder, element);
  PlaceHolder.SourceI = element;
}

function itemMoved(newPos, element, eventObj)
{
  eventObj = eventObj ? eventObj : window.event;
  var yPos = newPos.Y + (eventObj.layerY ? eventObj.layerY : eventObj.offsetY);

  var temp;
  var bestItem = "end";
  for (var i=0; i<List.childNodes.length; i++)
  {
    if (List.childNodes[i].className == "ui-el-sortlist-item")
    {
//      temp = parseInt(List.childNodes[i].style.height);
        temp = List.childNodes[i].offsetHeight;
      if (temp/2 >= yPos)
      {
        bestItem = List.childNodes[i];
        break;
      }    
      yPos -= temp;
    }
  }
 
  if(bestItem == PlaceHolder || bestItem == PlaceHolder.SourceI)
    return;
 
  PlaceHolder.SourceI = bestItem;
  if(bestItem != "end")
    List.insertBefore(PlaceHolder, List.childNodes[i]);
  else
    List.appendChild(PlaceHolder);
}

function itemDragEnd(element)
{
  if(PlaceHolder.SourceI != null)
  {
    PlaceHolder.SourceI = null;  
    List.replaceChild(element, PlaceHolder);
  }

  element.className = 'ui-el-sortlist-item';
  element.style.top = '0px';
  element.style.left = '0px';
}

/* End of licensed code */

function ui_dumpSortList(id) {
  res = '';
 
  List = document.getElementById(id);
  for (i=0; i<List.children.length; i++)
    res += '|' + List.children[i].id;
 
  return res.substr(1)
  
}
