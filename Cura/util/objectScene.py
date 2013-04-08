import random
import numpy

class _objectOrder(object):
	def __init__(self, order, todo):
		self.order = order
		self.todo = todo

class _objectOrderFinder(object):
	def __init__(self, scene, offset):
		self._scene = scene
		self._offset = offset - numpy.array([0.1,0.1])
		self._objs = scene.objects()
		self._leftToRight = True
		self._frontToBack = True
		initialList = []
		for n in xrange(0, len(self._objs)):
			if scene.checkPlatform(self._objs[n]):
				initialList.append(n)
		if len(initialList) == 0:
			self.order = []
			return
		self._todo = [_objectOrder([], initialList)]
		while len(self._todo) > 0:
			current = self._todo.pop()
			for addIdx in current.todo:
				if not self._checkHitFor(addIdx, current.order):
					todoList = current.todo[:]
					todoList.remove(addIdx)
					order = current.order[:] + [addIdx]
					if len(todoList) == 0:
						self._todo = None
						self.order = order
						return
					self._todo.append(_objectOrder(order, todoList))
		self.order = None

	def _checkHitFor(self, addIdx, others):
		for idx in others:
			if self._checkHit(addIdx, idx):
				return True
		return False

	def _checkHit(self, addIdx, idx):
		addPos = self._scene._objectList[addIdx].getPosition()
		addSize = self._scene._objectList[addIdx].getSize()
		pos = self._scene._objectList[idx].getPosition()
		size = self._scene._objectList[idx].getSize()

		if self._leftToRight:
			if addPos[0] + addSize[0] / 2 + self._offset[0] <= pos[0] - size[0] / 2:
				return False
		else:
			if addPos[0] - addSize[0] / 2 - self._offset[0] <= pos[0] + size[0] / 2:
				return False

		if self._frontToBack:
			if addPos[1] - addSize[1] / 2 - self._offset[1] >= pos[1] + size[1] / 2:
				return False
		else:
			if addPos[1] + addSize[1] / 2 + self._offset[1] >= pos[1] - size[1] / 2:
				return False

		return True

class Scene(object):
	def __init__(self):
		self._objectList = []
		self._sizeOffsets = numpy.array([0.0,0.0], numpy.float32)
		self._machineSize = numpy.array([100,100,100], numpy.float32)
		self._headOffsets = numpy.array([18.0,18.0], numpy.float32)

	def setMachineSize(self, machineSize):
		self._machineSize = machineSize

	def setSizeOffsets(self, sizeOffsets):
		self._sizeOffsets = sizeOffsets

	def getObjectExtend(self):
		return self._sizeOffsets + self._headOffsets

	def objects(self):
		return self._objectList

	def add(self, obj):
		self._findFreePositionFor(obj)
		self._objectList.append(obj)
		self.pushFree()

	def remove(self, obj):
		self._objectList.remove(obj)

	def merge(self, obj1, obj2):
		self.remove(obj2)
		obj1._meshList += obj2._meshList
		obj1.processMatrix()

	def pushFree(self):
		n = 1000
		while self._pushFree():
			n -= 1
			if n < 0:
				return

	def arrangeAll(self):
		oldList = self._objectList
		self._objectList = []
		for obj in oldList:
			obj.setPosition(numpy.array([0,0], numpy.float32))
			self.add(obj)

	def centerAll(self):
		minPos = numpy.array([9999999,9999999], numpy.float32)
		maxPos = numpy.array([-9999999,-9999999], numpy.float32)
		for obj in self._objectList:
			pos = obj.getPosition()
			size = obj.getSize()
			minPos[0] = min(minPos[0], pos[0] - size[0] / 2)
			minPos[1] = min(minPos[1], pos[1] - size[1] / 2)
			maxPos[0] = max(maxPos[0], pos[0] + size[0] / 2)
			maxPos[1] = max(maxPos[1], pos[1] + size[1] / 2)
		offset = -(maxPos + minPos) / 2
		for obj in self._objectList:
			obj.setPosition(obj.getPosition() + offset)

	def printOrder(self):
		order = _objectOrderFinder(self, self._headOffsets + self._sizeOffsets).order
		if order is None:
			print "ODD! Cannot find out proper printing order!!!"
			for obj in self._objectList:
				print obj.getPosition(), obj.getSize()
		return order

	def _pushFree(self):
		for a in self._objectList:
			for b in self._objectList:
				if not self._checkHit(a, b):
					continue
				posDiff = a.getPosition() - b.getPosition()
				if posDiff[0] == 0.0 and posDiff[1] == 0.0:
					posDiff[1] = 1.0
				if abs(posDiff[0]) > abs(posDiff[1]):
					axis = 0
				else:
					axis = 1
				aPos = a.getPosition()
				bPos = b.getPosition()
				center = (aPos[axis] + bPos[axis]) / 2
				distance = (a.getSize()[axis] + b.getSize()[axis]) / 2 + 0.1 + self._sizeOffsets[axis] + self._headOffsets[axis]
				if posDiff[axis] < 0:
					distance = -distance
				aPos[axis] = center + distance / 2
				bPos[axis] = center - distance / 2
				a.setPosition(aPos)
				b.setPosition(bPos)
				return True
		return False

	def _checkHit(self, a, b):
		if a == b:
			return False
		posDiff = a.getPosition() - b.getPosition()
		if abs(posDiff[0]) < (a.getSize()[0] + b.getSize()[0]) / 2 + self._sizeOffsets[0] + self._headOffsets[0]:
			if abs(posDiff[1]) < (a.getSize()[1] + b.getSize()[1]) / 2 + self._sizeOffsets[1] + self._headOffsets[1]:
				return True
		return False

	def checkPlatform(self, obj):
		p = obj.getPosition()
		s = obj.getSize()[0:2] / 2 + self._sizeOffsets
		if p[0] - s[0] < -self._machineSize[0] / 2:
			return False
		if p[0] + s[0] > self._machineSize[0] / 2:
			return False
		if p[1] - s[1] < -self._machineSize[1] / 2:
			return False
		if p[1] + s[1] > self._machineSize[1] / 2:
			return False
		return True

	def _findFreePositionFor(self, obj):
		posList = []
		for a in self._objectList:
			p = a.getPosition()
			s = (a.getSize()[0:2] + obj.getSize()[0:2]) / 2 + self._sizeOffsets + self._headOffsets
			posList.append(p + s * ( 1.0, 1.0))
			posList.append(p + s * ( 0.0, 1.0))
			posList.append(p + s * (-1.0, 1.0))
			posList.append(p + s * ( 1.0, 0.0))
			posList.append(p + s * (-1.0, 0.0))
			posList.append(p + s * ( 1.0,-1.0))
			posList.append(p + s * ( 0.0,-1.0))
			posList.append(p + s * (-1.0,-1.0))

		best = None
		bestDist = None
		for p in posList:
			obj.setPosition(p)
			ok = True
			for a in self._objectList:
				if self._checkHit(a, obj):
					ok = False
					break
			if not ok:
				continue
			dist = numpy.linalg.norm(p)
			if not self.checkPlatform(obj):
				dist *= 3
			if best is None or dist < bestDist:
				best = p
				bestDist = dist
		if best is not None:
			obj.setPosition(best)
