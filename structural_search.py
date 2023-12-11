import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer

import torch
import numpy as np

from sklearn.neighbors import NearestNeighbors

EMB_DIMS = 384
FTS_WIGHTS = [.1, .35,  .1, .05, .05, .35]

device = "cuda" if torch.cuda.is_available() else "cpu"


def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    similarity = dot_product / (norm_v1 * norm_v2)
    return similarity[0]

class Student:

    embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    def __init__(self, faculty: str, about: str, activities: str, books: str, games: str, interests: str, city: str):
       self.faculty, self.about, self.activities, self.books, self.games, self.interests, self.city = \
          faculty, about, activities, books, games, interests, city

       self.ff_vector = np.zeros((EMB_DIMS, ), dtype=float)

       self.ff_vector = self._make_embedding()

    def _make_embedding(self):
       ff_vector = self._eval_part_embedding(self.faculty, FTS_WIGHTS[0])
       ff_vector += self._eval_part_embedding(self.about, FTS_WIGHTS[1])
       ff_vector += self._eval_part_embedding(self.activities, FTS_WIGHTS[2])
       ff_vector += self._eval_part_embedding(self.books, FTS_WIGHTS[3])
       ff_vector += self._eval_part_embedding(self.games, FTS_WIGHTS[4])
       ff_vector += self._eval_part_embedding(self.interests, FTS_WIGHTS[5])
       return ff_vector

    def _eval_part_embedding(self, text: str, weight: float):
      if text == "":
        return np.zeros((EMB_DIMS, ), dtype=float)

      embidding = Student.embedding_model.encode(text, convert_to_tensor=True)
      embidding = embidding.to(device).cpu().numpy()
      return weight*embidding

class Recommendation:
    def __init__(self, city: str, facult: str):
      self.city = city
      self.facult = facult

class Faculty:
   def __init__(self, students):
     self.students = students
     self.faculty_index = self._make_index()

   def _make_index(self):
     if not len(self.students):
       return np.zeros((0, EMB_DIMS), float)

     if len(self.students) == 1:
      features = self.students[0].ff_vector
      features = np.reshape(features, (1, -1))
      return features

     features = np.array([student.ff_vector for student in self.students])
     return np.reshape(np.mean(features, axis=0), (1, -1))

   def unique_recomends(self):
     ustudents = self._uniquefication()
     ustudents = self.arrange_students(ustudents)
     return [ Recommendation(student.city, student.faculty) for student in ustudents]

   def arrange_students(self, students):
      similarities = np.array([cosine_similarity(self.faculty_index, student.ff_vector) for student in students])
      sorted_indices = np.argsort(similarities)[::-1]
      sorted_students = [students[i] for i in sorted_indices]
      return sorted_students

   def _uniquefication(self):
     seen_combinations = set()
     unique_students = []

     for student in self.students:
        combination = (student.faculty, student.city)

        if combination not in seen_combinations:
           seen_combinations.add(combination)
           unique_students.append(student)
     return unique_students


def make_faculty_dates(df, column_name="faculty_name"):
  f_names = df[column_name].unique()
  faculties = []
  for faculty in f_names:
     faculty_df = df[df[column_name] == faculty]
     if len(faculty_df) < 3:
        continue

     students=[]
     for idx, record in faculty_df.iterrows():
         student = Student(
             faculty=record['faculty_name'],
             about=record['about'],
             activities=record['activities'],
             books=record['books'],
             games=record['games'],
             interests=record['interests'],
             city=record['city_title']
         )
         students.append(student)
     faculties.append(Faculty(students))
  return faculties


FEATURES = ['country_title', 'city_title', 'faculty_name', 'about', 'activities', 'books', 'games', 'interests']
N_RECOM = 20

if __name__ == "__main__":

  '''
  test_student = Student(
      faculty="физико-математический",
      about="люблю жизнь как есть",
      books="вся фантастика особенно Лем",
      games="Сталкер",
      interests="симплексная геометрия, диффуры",
      activities="походы",
      city="Питер")

  test_student2 = Student(
      faculty="физика твердого тела",
      about="",
      books="вся фантастика особенно Лем",
      games="DOTA2",
      interests="матан",
      activities="походы",
      city="Питер")

  faculty = Faculty([test_student, test_student2])
  for recomd in faculty.unique_recomends():
      print(f'City: {recomd.city} Facult: {recomd.facult}' )
  '''


  '''
  df_raw = pd.read_csv("h_raw_data.1500k.records.csv")
  print(df_raw.info())
  df_raw["faculty_name"].replace('', np.nan, inplace=True)
  df = df_raw.dropna(subset=["faculty_name"])
  df.drop(
        columns=['record_id', 'time_created', 'time_updated', 'meta_data', 'page_number', 'deactivated'],
        inplace=True)

  df.drop_duplicates(inplace=True)
  df.reset_index(drop=True, inplace=True)
  print(df.info())

  for col in FEATURES:
      df[col].fillna('', inplace=True)

  FACULTIES = make_faculty_dates(df)

  with open('facs.pckl', 'wb') as f:
     pickle.dump(FACULTIES, f)
  '''
  with open('facs.pckl', 'rb') as f:
    FACULTIES = pickle.load(f)

  SEARCH_SPACE = np.array([faculty.faculty_index for faculty in FACULTIES])
  SEARCH_SPACE = np.squeeze(SEARCH_SPACE)
  knn = NearestNeighbors(n_neighbors=N_RECOM, metric='cosine')
  knn.fit(SEARCH_SPACE)

  query = Student(
      about="люблю компьютеры, машинное обучение и программирование",
      books="Стивен Хоккинг, Гарри Поттер, Достоевский, Стругацкие, 12 стульев",
      games="GTA 5, Dota 2, Minecraft",
      interests="Музыка, кино, программирование",
      activities="велосипед, гитара, плавание",
      faculty=" ",
      city="Mocква"
  )

  query = Student(
      about="защищаю данные",
      books="Страуструп, x64 Assembly Language",
      games="Kerbal Space Program",
      interests="эллиптические кривые, дата майнинг",
      activities="походы, яхтинг",
      faculty=" ",
      city="Mocква"
  )

  distances, ids = knn.kneighbors([query.ff_vector])
  ids = np.flip(np.squeeze(ids))
  distances = np.flip(np.squeeze(distances))
  for id in range(len(ids)):
    faculty = FACULTIES[ids[id]]
    for recomd in faculty.unique_recomends():
        print(f'City: {recomd.city} Facult: {recomd.facult} Dist {distances[id]}')






