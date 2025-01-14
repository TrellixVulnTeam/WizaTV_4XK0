# coding=utf-8
import os, sys
import xbmc, xbmcaddon, xbmcgui, xbmcplugin, urllib, xbmcvfs
import xml.etree.ElementTree as xmltree
import cPickle as pickle
import cProfile
import pstats
import random
import time
import calendar
import thread
from time import gmtime, strftime
from datetime import datetime
from traceback import print_exc

if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

ADDON        = xbmcaddon.Addon()
ADDONID      = ADDON.getAddonInfo('id').decode( 'utf-8' )
ADDONVERSION = ADDON.getAddonInfo('version')
LANGUAGE     = ADDON.getLocalizedString
CWD          = ADDON.getAddonInfo('path').decode("utf-8")
ADDONNAME    = ADDON.getAddonInfo('name').decode("utf-8")
RESOURCE     = xbmc.translatePath( os.path.join( CWD, 'resources', 'lib' ) ).decode("utf-8")
DATAPATH     = os.path.join( xbmc.translatePath( "special://profile/" ).decode( 'utf-8' ), "addon_data", ADDONID )
MASTERPATH   = os.path.join( xbmc.translatePath( "special://masterprofile/" ).decode( 'utf-8' ), "addon_data", ADDONID )

sys.path.append(RESOURCE)

import xmlfunctions, datafunctions, library, nodefunctions
XML = xmlfunctions.XMLFunctions()
DATA = datafunctions.DataFunctions()
LIBRARY = library.LibraryFunctions()
NODE = nodefunctions.NodeFunctions()

hashlist = []

def log(txt):
    if ADDON.getSetting( "enable_logging" ) == "true":
        if isinstance (txt,str):
            txt = txt.decode('utf-8')
        message = u'%s: %s' % (ADDONID, txt)
        xbmc.log(msg=message.encode('utf-8'), level=xbmc.LOGDEBUG)
        
class Main:
    # MAIN ENTRY POINT
    def __init__(self):
        self._parse_argv()
        self.WINDOW = xbmcgui.Window(10000)
        
        # Create data and master paths if not exists
        if not xbmcvfs.exists(DATAPATH):
            xbmcvfs.mkdir(DATAPATH)
        if not xbmcvfs.exists(MASTERPATH):
            xbmcvfs.mkdir(MASTERPATH)
        
        # Perform action specified by user
        if not self.TYPE:
            line1 = "This addon is for skin developers, and requires skin support"
            xbmcgui.Dialog().ok(ADDONNAME, line1)
            
        if self.TYPE=="buildxml":
            XML.buildMenu( self.MENUID, self.GROUP, self.LEVELS, self.MODE, self.OPTIONS, self.MINITEMS )
            
        if self.TYPE=="launch":
            xbmcplugin.setResolvedUrl( handle=int( sys.argv[1]), succeeded=False, listitem=xbmcgui.ListItem() )
            self._launch_shortcut( self.PATH )
        if self.TYPE=="launchpvr":
            xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Player.Open", "params": { "item": {"channelid": ' + self.CHANNEL + '} } }')
        if self.TYPE=="manage":
            self._manage_shortcuts( self.GROUP, self.DEFAULTGROUP, self.NOLABELS, self.GROUPNAME )
            
        if self.TYPE=="hidesubmenu":
            self._hidesubmenu( self.MENUID )
        if self.TYPE=="resetlist":
            self._resetlist( self.MENUID, self.NEXTACTION )
            
        if self.TYPE=="shortcuts":
            # We're just going to choose a shortcut, and save its details to the given
            # skin labels

            # Load library shortcuts in thread
            thread.start_new_thread( LIBRARY.loadAllLibrary, () )
            
            if self.GROUPING is not None:
                selectedShortcut = LIBRARY.selectShortcut( "", grouping = self.GROUPING, custom = self.CUSTOM, showNone = self.NONE )
            else:
                selectedShortcut = LIBRARY.selectShortcut( "", custom = self.CUSTOM, showNone = self.NONE )
            
            # Now set the skin strings
            if selectedShortcut is not None and selectedShortcut.getProperty( "Path" ):
                path = selectedShortcut.getProperty( "Path" )

                if selectedShortcut.getProperty( "chosenPath" ):
                    path = selectedShortcut.getProperty( "chosenPath" )

                if path.startswith( "pvr-channel://" ):
                    path = "RunScript(script.skinshortcuts,type=launchpvr&channel=" + path.replace( "pvr-channel://", "" ) + ")"
                if self.LABEL is not None and selectedShortcut.getLabel() != "":
                    xbmc.executebuiltin( "Skin.SetString(" + self.LABEL + "," + selectedShortcut.getLabel() + ")" )
                if self.ACTION is not None:
                    xbmc.executebuiltin( "Skin.SetString(" + self.ACTION + "," + path + " )" )
                if self.SHORTCUTTYPE is not None:
                    xbmc.executebuiltin( "Skin.SetString(" + self.SHORTCUTTYPE + "," + selectedShortcut.getLabel2() + ")" )
                if self.THUMBNAIL is not None and selectedShortcut.getProperty( "icon" ):
                    xbmc.executebuiltin( "Skin.SetString(" + self.THUMBNAIL + "," + selectedShortcut.getProperty( "icon" ) + ")" )
                if self.THUMBNAIL is not None and selectedShortcut.getProperty( "thumbnail" ):
                    xbmc.executebuiltin( "Skin.SetString(" + self.THUMBNAIL + "," + selectedShortcut.getProperty( "thumbnail" ) + ")" )
                if self.LIST is not None:
                    xbmc.executebuiltin( "Skin.SetString(" + self.LIST + "," + DATA.getListProperty( path ) + ")" )
            elif selectedShortcut is not None and selectedShortcut.getLabel() == "::NONE::":
                # Clear the skin strings
                if self.LABEL is not None:
                    xbmc.executebuiltin( "Skin.Reset(" + self.LABEL + ")" )
                if self.ACTION is not None:
                    xbmc.executebuiltin( "Skin.Reset(" + self.ACTION + " )" )
                if self.SHORTCUTTYPE is not None:
                    xbmc.executebuiltin( "Skin.Reset(" + self.SHORTCUTTYPE + ")" )
                if self.THUMBNAIL is not None:
                    xbmc.executebuiltin( "Skin.Reset(" + self.THUMBNAIL + ")" )
                if self.THUMBNAIL is not None:
                    xbmc.executebuiltin( "Skin.Reset(" + self.THUMBNAIL + ")" )
                if self.LIST is not None:
                    xbmc.executebuiltin( "Skin.Reset(" + self.LIST + ")" )

        if self.TYPE=="widgets":
            # We're just going to choose a widget, and save its details to the given
            # skin labels

            # Load library shortcuts in thread
            thread.start_new_thread( LIBRARY.loadAllLibrary, () )

            # Check if we should show the custom option (if the relevant widgetPath skin string is provided and isn't empty)
            showCustom = False
            if self.WIDGETPATH and xbmc.getCondVisibility( "!IsEmpty(Skin.String(%s))" %( self.WIDGETPATH ) ):
                showCustom = True
            
            if self.GROUPING:
                if self.GROUPING.lower() == "default":
                    selectedShortcut = LIBRARY.selectShortcut( "", custom = showCustom, showNone = self.NONE )    
                else:
                    selectedShortcut = LIBRARY.selectShortcut( "", grouping = self.GROUPING, custom = showCustom, showNone = self.NONE )
            else:
                selectedShortcut = LIBRARY.selectShortcut( "", grouping = "widget", custom = showCustom, showNone = self.NONE )
            
            # Now set the skin strings
            if selectedShortcut is None:
                # The user cancelled
                return

            elif selectedShortcut.getProperty( "Path" ) and selectedShortcut.getProperty( "custom" ) == "true":
                # The user updated the path - so we just set that property
                xbmc.executebuiltin( "Skin.SetString(%s,%s)" %( self.WIDGETPATH, urllib.unquote( selectedShortcut.getProperty( "Path" ) ) ) )

            elif selectedShortcut.getProperty( "Path" ):
                # The user selected the widget they wanted
                if self.WIDGET:
                    if selectedShortcut.getProperty( "widget" ):
                        xbmc.executebuiltin( "Skin.SetString(%s,%s)" %( self.WIDGET, selectedShortcut.getProperty( "widget" ) ) )
                    else:
                        xbmc.executebuiltin( "Skin.Reset(%s)" %( self.WIDGET ) )
                if self.WIDGETTYPE:
                    if selectedShortcut.getProperty( "widgetType" ):
                        xbmc.executebuiltin( "Skin.SetString(%s,%s)" %( self.WIDGETTYPE, selectedShortcut.getProperty( "widgetType" ) ) )
                    else:
                        xbmc.executebuiltin( "Skin.Reset(%s)" %( self.WIDGETTYPE ) )
                if self.WIDGETNAME:
                    if selectedShortcut.getProperty( "widgetName" ):
                        xbmc.executebuiltin( "Skin.SetString(%s,%s)" %( self.WIDGETNAME, selectedShortcut.getProperty( "widgetName" ) ) )
                    else:
                        xbmc.executebuiltin( "Skin.Reset(%s)" %( self.WIDGETNAME ) )
                if self.WIDGETTARGET:
                    if selectedShortcut.getProperty( "widgetTarget" ):
                        xbmc.executebuiltin( "Skin.SetString(%s,%s)" %( self.WIDGETTARGET, selectedShortcut.getProperty( "widgetTarget" ) ) )
                    else:
                        xbmc.executebuiltin( "Skin.Reset(%s)" %( self.WIDGETTARGET ) )
                if self.WIDGETPATH:
                    if selectedShortcut.getProperty( "widgetPath" ):
                        xbmc.executebuiltin( "Skin.SetString(%s,%s)" %( self.WIDGETPATH, urllib.unquote( selectedShortcut.getProperty( "widgetPath" ) ) ) )
                    else:
                        xbmc.executebuiltin( "Skin.Reset(%s)" %( self.WIDGETPATH ) )

            elif selectedShortcut.getLabel() == "::NONE::":
                # Clear the skin strings
                if self.WIDGET is not None:
                    xbmc.executebuiltin( "Skin.Reset(" + self.WIDGET + ")" )
                if self.WIDGETTYPE is not None:
                    xbmc.executebuiltin( "Skin.Reset(" + self.WIDGETTYPE + " )" )
                if self.WIDGETNAME is not None:
                    xbmc.executebuiltin( "Skin.Reset(" + self.WIDGETNAME + ")" )
                if self.WIDGETTARGET is not None:
                    xbmc.executebuiltin( "Skin.Reset(" + self.WIDGETTARGET + ")" )
                if self.WIDGETPATH is not None:
                    xbmc.executebuiltin( "Skin.Reset(" + self.WIDGETPATH + ")" )

        if self.TYPE=="context":
            # Context menu addon asking us to add a folder to the menu
            if not xbmc.getCondVisibility( "Skin.HasSetting(SkinShortcuts-FullMenu)" ):
                xbmcgui.Dialog().ok(ADDONNAME, ADDON.getLocalizedString(32116))
            else:
                NODE.addToMenu( self.CONTEXTFILENAME, self.CONTEXTLABEL, self.CONTEXTICON, self.CONTEXTCONTENT, self.CONTEXTWINDOW, DATA )

        if self.TYPE=="setProperty":
            # External request to set properties of a menu item
            NODE.setProperties( self.PROPERTIES, self.VALUES, self.LABELID, self.GROUPNAME, DATA )
                
        if self.TYPE=="resetall":
            # Tell XBMC not to try playing any media
            try:
                xbmcplugin.setResolvedUrl( handle=int( sys.argv[1]), succeeded=False, listitem=xbmcgui.ListItem() )
            except:
                log( "Not launched from a list item" )
            self._reset_all_shortcuts()

    def _parse_argv( self ):
        try:
            params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
            self.TYPE = params.get( "type", "" )
        except:
            #print_exc()
            try:
                params = dict( arg.split( "=" ) for arg in sys.argv[ 2 ].split( "&" ) )
                self.TYPE = params.get( "?type", "" )
            except:
                self.TYPE = ""
                params = {}
        
        self.GROUP = params.get( "group", "" )
        self.GROUPNAME = params.get( "groupname", None )
        self.GROUPING = params.get( "grouping", None )
        self.PATH = params.get( "path", "" )
        self.MENUID = params.get( "mainmenuID", "0" )
        self.NEXTACTION = params.get( "action", "0" )
        self.LEVELS = params.get( "levels", "0" )
        self.MODE = params.get( "mode", None )
        self.CHANNEL = params.get( "channel", None )
        
        # Properties when using LIBRARY._displayShortcuts
        self.LABEL = params.get( "skinLabel", None )
        self.ACTION = params.get( "skinAction", None )
        self.SHORTCUTTYPE = params.get( "skinType", None )
        self.THUMBNAIL = params.get( "skinThumbnail", None )
        self.LIST = params.get( "skinList", None )
        self.CUSTOM = params.get( "custom", "False" )
        self.NONE = params.get( "showNone", "False" )

        self.WIDGET = params.get( "skinWidget", None )
        self.WIDGETTYPE = params.get( "skinWidgetType", None )
        self.WIDGETNAME = params.get( "skinWidgetName", None )
        self.WIDGETTARGET = params.get( "skinWidgetTarget", None )
        self.WIDGETPATH = params.get( "skinWidgetPath", None )

        if self.CUSTOM == "True" or self.CUSTOM == "true":
            self.CUSTOM = True
        else:
            self.CUSTOM = False
        if self.NONE == "True" or self.NONE == "true":
            self.NONE = True
        else:
            self.NONE = False
        
        self.NOLABELS = params.get( "nolabels", "false" ).lower()
        self.OPTIONS = params.get( "options", "" ).split( "|" )
        self.MINITEMS = int( params.get( "minitems", "0" ) )
        self.WARNING = params.get( "warning", None )
        self.DEFAULTGROUP = params.get( "defaultGroup", None )

        # Properties from context menu addon
        self.CONTEXTFILENAME = urllib.unquote( params.get( "filename", "" ) )
        self.CONTEXTLABEL = params.get( "label", "" )
        self.CONTEXTICON = params.get( "icon", "" )
        self.CONTEXTCONTENT = params.get( "content", "" )
        self.CONTEXTWINDOW = params.get( "window", "" )

        # Properties from external request to set properties
        self.PROPERTIES = urllib.unquote( params.get( "property", "" ) )
        self.VALUES = urllib.unquote( params.get( "value", "" ) )
        self.LABELID = params.get( "labelID", "" )
    
    
    # -----------------
    # PRIMARY FUNCTIONS
    # -----------------

    def _launch_shortcut( self, path ):
        action = urllib.unquote( self.PATH )
        
        if action.find("::MULTIPLE::") == -1:
            # Single action, run it
            xbmc.executebuiltin( action )
        else:
            # Multiple actions, separated by |
            actions = action.split( "|" )
            for singleAction in actions:
                if singleAction != "::MULTIPLE::":
                    xbmc.executebuiltin( singleAction )
        
    
    def _manage_shortcuts( self, group, defaultGroup, nolabels, groupname ):
        homeWindow = xbmcgui.Window( 10000 )
        if homeWindow.getProperty( "skinshortcuts-loading" ) and int( calendar.timegm( gmtime() ) ) - int( homeWindow.getProperty( "skinshortcuts-loading" ) ) <= 5:
            return

        homeWindow.setProperty( "skinshortcuts-loading", str( calendar.timegm( gmtime() ) ) )
        import gui
        ui= gui.GUI( "script-skinshortcuts.xml", CWD, "default", group=group, defaultGroup=defaultGroup, nolabels=nolabels, groupname=groupname )
        ui.doModal()
        del ui   
        
        # Update home window property (used to automatically refresh type=settings)
        homeWindow.setProperty( "skinshortcuts",strftime( "%Y%m%d%H%M%S",gmtime() ) )
        
        # Clear window properties for this group, and for backgrounds, widgets, properties
        homeWindow.clearProperty( "skinshortcuts-" + group )        
        homeWindow.clearProperty( "skinshortcutsWidgets" )        
        homeWindow.clearProperty( "skinshortcutsCustomProperties" )        
        homeWindow.clearProperty( "skinshortcutsBackgrounds" )        
        
        
    def _reset_all_shortcuts( self ):
        log( "### Resetting all shortcuts" )
        dialog = xbmcgui.Dialog()
        
        shouldRun = None
        if self.WARNING is not None and self.WARNING.lower() == "false":
            shouldRun = True
        
        # Ask the user if they're sure they want to do this
        if shouldRun is None:
            shouldRun = dialog.yesno( LANGUAGE( 32037 ), LANGUAGE( 32038 ) )
        
        if shouldRun:
            isShared = DATA.checkIfMenusShared()
            log( repr( isShared ) )
            for files in xbmcvfs.listdir( DATAPATH ):
                # Try deleting all shortcuts
                if files:
                    for file in files:
                        deleteFile = False
                        if file == "settings.xml":
                            continue
                        if isShared:
                            deleteFile = True
                        elif file.startswith( xbmc.getSkinDir() ) and ( file.endswith( ".properties" ) or file.endswith( ".DATA.xml" ) ):
                            deleteFile = True

                        #if file != "settings.xml" and ( not isShared or file.startswith( "%s-" %( xbmc.getSkinDir() ) ) ) or file == "%s.properties" %( xbmc.getSkinDir() ):
                        if deleteFile:
                            file_path = os.path.join( DATAPATH, file.decode( 'utf-8' ) ).encode( 'utf-8' )
                            if xbmcvfs.exists( file_path ):
                                try:
                                    xbmcvfs.delete( file_path )
                                except:
                                    print_exc()
                                    log( "### ERROR could not delete file %s" % file )
                        else:
                            log( "Not deleting file %s" %[ file ] )
        
            # Update home window property (used to automatically refresh type=settings)
            xbmcgui.Window( 10000 ).setProperty( "skinshortcuts",strftime( "%Y%m%d%H%M%S",gmtime() ) )   
    
    # Functions for providing whoe menu in single list
    def _hidesubmenu( self, menuid ):
        count = 0
        while xbmc.getCondVisibility( "!IsEmpty(Container(" + menuid + ").ListItem(" + str( count ) + ").Property(isSubmenu))" ):
            count -= 1
            
        if count != 0:
            xbmc.executebuiltin( "Control.Move(" + menuid + "," + str( count ) + " )" )
        
        xbmc.executebuiltin( "ClearProperty(submenuVisibility, 10000)" )
        
    def _resetlist( self, menuid, action ):
        count = 0
        while xbmc.getCondVisibility( "!IsEmpty(Container(" + menuid + ").ListItemNoWrap(" + str( count ) + ").Label)" ):
            count -= 1
            
        count += 1
            
        if count != 0:
            xbmc.executebuiltin( "Control.Move(" + menuid + "," + str( count ) + " )" )
            
        xbmc.executebuiltin( urllib.unquote( action ) )
        
if ( __name__ == "__main__" ):
    log('script version %s started' % ADDONVERSION)
    
    # Profiling
    #filename = os.path.join( DATAPATH, strftime( "%Y%m%d%H%M%S",gmtime() ) + "-" + str( random.randrange(0,100000) ) + ".log" )
    #cProfile.run( 'Main()', filename )
    
    #stream = open( filename + ".txt", 'w')
    #p = pstats.Stats( filename, stream = stream )
    #p.sort_stats( "cumulative" )
    #p.print_stats()
    
    # No profiling
    Main()
    
    log('script stopped')
