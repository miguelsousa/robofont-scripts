 #coding=utf-8
import json
import inspect

from booleanOperations.booleanGlyph import BooleanGlyph
from fontTools.pens.basePen import BasePen
from robofab.world import RGlyph
from errorGlyph import ErrorGlyph
from cleanPen import CleanPointPen

def getFileName(path):
    fileName = path.split('/')
    return fileName[-1][:-3]

class GlyphFilter(object):
    """
    Filter object initiated with a robofab pen and, if need be, arguments for that pen,
    and then acts like a filter function returning a filtered glyph.

    >>> from robofab.pens.filterPen import FlattenPen
    >>> filter = GlyphFilter(FlattenPen)
    >>> filteredGlyph = filter(glyph, glyph.getParent(), approximateSegmentLength=25)
    """
    def __init__(self, *filterTuples):
        self.filterObjects = []
        self.filterArguments = {}
        self.modes = {}
        self.initialSources = {}
        for filterObject, filterArguments, mode, initialSource in filterTuples:
            self.filterObjects.append(filterObject)
            self.filterArguments[filterObject] = filterArguments
            self.modes[filterObject] = mode
            self.initialSources[filterObject] = initialSource

    def __call__(self, glyph, font=None, **globalArguments):
        filterObjects = self.filterObjects
        outputGlyph = self.cleanGlyph(glyph)
        initialGlyph = self.cleanGlyph(glyph)

        for filterObject in filterObjects:
            filterArguments = self.filterArguments[filterObject]
            mode = self.modes[filterObject]
            initialSource = self.initialSources[filterObject]
            if initialSource == True:
                glyphToProcess = initialGlyph
            else:
                glyphToProcess = outputGlyph
            arguments = {argumentName: argumentValue for argumentName, argumentValue in globalArguments.items() if argumentName in filterArguments}
            filteredGlyph = self.processGlyph(filterObject, glyphToProcess, font=None, **arguments)
            if mode is None:
                outputGlyph = filteredGlyph
            elif mode == 'add':
                pen = outputGlyph.getPen()
                filteredGlyph.draw(pen)
            elif mode in ['union','difference','intersection']:
                try:
                    b1 = BooleanGlyph(outputGlyph)
                    b2 = BooleanGlyph(filteredGlyph)
                    action = getattr(b1, mode)
                    outputGlyph = action(b2)
                except:
                    outputGlyph = ErrorGlyph('boolean')
        return outputGlyph

    def processGlyph(self, filterObject, glyph, font, **arguments):
        filteredGlyph = RGlyph()
        filteredGlyph.width = glyph.width

        if inspect.isfunction(filterObject):
            try:
                filteredGlyph.appendGlyph(glyph)
                filteredGlyph = filterObject(filteredGlyph, **arguments)
                if filteredGlyph is None:
                    filteredGlyph = glyph
            except Exception as e:
                print u'PenBallWizard — GlyphFilter Error (function): {0}'.format(e)
                filteredGlyph = ErrorGlyph()

        else:
            try:
                drawingPen = filteredGlyph.getPen()
                filterPen = filterObject(drawingPen, **arguments)
                glyph.draw(filterPen)

            except Exception as e:
                print u'PenBallWizard — GlyphFilter Error (pen): {0}'.format(e)
                filteredGlyph = ErrorGlyph()

        return filteredGlyph

    def cleanGlyph(self, glyph):
        cleanGlyph = RGlyph()
        cleanGlyph.width = glyph.width
        pen = cleanGlyph.getPointPen()
        cleanPen = CleanPointPen()
        glyph.drawPoints(cleanPen)
        cleanPen.extract(pen)
        return cleanGlyph

if __name__ == '__main__':

    try:
        import fontTools
        import robofab
        from robofab.pens.filterPen import ThresholdPen
        import defcon
        from defcon import Glyph

        import unittest

        class GlyphFilterTest(unittest.TestCase):

            def setUp(self):
                testGlyph = Glyph()
                pen = testGlyph.getPen()
                self.drawTestGlyph(pen)
                self.testGlyph = testGlyph

            def drawTestGlyph(self, pen):
                pen.moveTo((10, 10))
                pen.lineTo((110, 10))
                pen.lineTo((110, 110))
                pen.lineTo((10, 110))
                pen.closePath()

            def test_GlyphFilterInit(self):
                thresholdFilter = GlyphFilter(ThresholdPen)
                testGlyph = self.testGlyph
                filteredGlyph = thresholdFilter(testGlyph, testGlyph.getParent(), threshold=20)

        unittest.main()

    except:
        pass