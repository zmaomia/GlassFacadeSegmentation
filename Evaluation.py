
import numpy as np
import os
from lib.read_data.OBJ_PARSER import *


class data_PARSER(OBJ_PARSER):
	def __init__(self, model_file):
		super(data_PARSER,self).__init__(model_file)

	def get_triangles(self):
		faces = self.get_faces()
		vertices = self.get_vertices()
		for index in faces:
			triangle = [vertices[index[0]-1], vertices[index[2]-1], vertices[index[4]-1]]
			triangle = np.array(triangle).astype(np.float32)
			triangle = tuple(map(str, triangle))
			self.triangles.append(triangle)
		return self.triangles, faces, vertices


def read_3D_segments(dirpath):
	segments = {}
	
	obj_files = os.listdir(dirpath)
	
	for obj_file in obj_files:
		
		model_file = os.path.join(dirpath, obj_file)
		parser = data_PARSER(model_file)
		triangles, faces, vertices = parser.get_triangles()
		segments[obj_file] = triangles
		
		# print('triangles number of %s is %d: '% (obj_file, len(triangles)))
	return segments



def evaluate(gt_segments, pred_segments, threshold = 0.5):
	
	pred_num = len(pred_segments.keys())
	gt_num = len(gt_segments.keys())

	print('pred_num:', pred_num)
	print('gt_num:', gt_num)

	total_precision = 0.0
	total_recall = 0.0
	total_iou = 0.0

	for obj in pred_segments.keys():

		print('----------------------------------------------')

		print('obj_name:', obj)
		pred_triangles = pred_segments[obj]
		pred_triangles_num = len(pred_triangles)

		gt_triangles = gt_segments[obj]
		gt_triangles_num = len(gt_triangles)

		print(pred_triangles_num, gt_triangles_num)

		intersection = len(set(pred_triangles).intersection(set(gt_triangles)))
		union = len(set(pred_triangles).union(set(gt_triangles)))

		precision = float(intersection/pred_triangles_num)
		recall = float(intersection/gt_triangles_num)
		iou = float(intersection/union)

		print('intersection:', intersection)
		print('union:', union)
		print('precision：', precision)
		print('recall：',  recall)
		print('iou：', iou)

		total_precision += precision
		total_recall += recall
		total_iou += iou

	mean_precision = float(total_precision/pred_num)
	mean_recall = float(total_recall/pred_num)
	mean_iou = float(total_iou/pred_num)

	print('****************************************')
 
	print('mean_precision', mean_precision)
	print('mean_recall',  mean_recall)
	print('mean_iou', mean_iou)


	
	exit(0)

	flag = np.zeros(gt_num)
	gt_names = list(gt_segments.keys())


	# pixel_level_precision, pixel_level_recall = 0.0, 0.0
	instance_tp = 0.0
	mIoU = []
	matches = []

	for pred_name, pred_segs in pred_segments.items():

		max_iou = 0
		match_gt_name = 0
		match_intersection = 0
		match_union = 0
		
		for gt_name, gt_segs in gt_segments.items():

			intersection = len(set(pred_segs).intersection(set(gt_segs)))
			union = len(set(pred_segs).union(set(gt_segs)))

			iou = intersection*1.0/union

			if iou>max_iou:
				max_iou = iou
				match_gt_name = gt_name
				match_intersection = intersection
				match_union = union
			
		if max_iou>=threshold:
			instance_tp +=1
			ind = gt_names.index(match_gt_name)
			flag[ind] = 1

			mIoU.append(max_iou)
			matches.append((pred_name, match_gt_name))

	instance_level_precision = instance_tp*1.0/pred_num
	instance_level_recall = np.sum(flag)*1.0 / gt_num
	mIoU = np.array(mIoU)
	mIoU = np.mean(mIoU)

	left_pred = set(pred_segments) - set(np.unique(matches))
	left_gt = set(gt_segments) - set(np.unique(matches))
	if len(left_gt) and len(left_pred):
		temp = []
		for left_p in left_pred:
			for left_g in left_gt:
				intersection = len(set(left_p).intersection(set(left_g)))
				union = len(set(left_p).union(set(left_g)))

				iou = intersection*1.0/union
				temp.append((left_g, left_p,iou))
		temp.sort(key = lambda  k:k[-1], reverse = True)
	
	return instance_level_precision, instance_level_recall, mIoU, matches




if __name__ == "__main__":

	gt_dirpath = './evaluation/label/'
	pred_dirpath = './3D Models/demo/demo/'

	gt_segments = read_3D_segments(gt_dirpath)
	pred_segments = read_3D_segments(pred_dirpath)

	instance_level_precision, instance_level_recall, mIOU, matches = evaluate(gt_segments, pred_segments)
	print(instance_level_precision, instance_level_recall, mIOU, matches, len(matches))


